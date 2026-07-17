#!/usr/bin/env python3
"""
PDF 解析器（基于 MinerU API）
"""

import os
import time
import zipfile
import io
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base import BaseParser, ParseResult, PageInfo


class PDFParser(BaseParser):
    """PDF 解析器（使用 MinerU 云端解析服务）"""

    MINERU_BASE_URL = "https://mineru.net/api/v4"

    def __init__(
        self,
        api_token: Optional[str] = None,
        model_version: str = "vlm",
        poll_interval: float = 3.0,
        poll_timeout: float = 300.0,
    ):
        super().__init__()
        self.api_token = api_token or os.environ.get("MINERU_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "未提供 MinerU API Token，请通过构造参数 api_token 或环境变量 "
                "MINERU_API_TOKEN 传入"
            )
        self.model_version = model_version
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

    def parse(self, file_path: Path, document_id: str) -> ParseResult:
        """解析 PDF 文件（通过 MinerU）"""
        self.clear_warnings()

        try:
            batch_id, file_name = self._upload_file(file_path)
        except Exception as e:
            self.add_warning(f"上传文件到 MinerU 失败: {e}")
            return self._create_empty_result(file_path, document_id)

        try:
            result_info = self._poll_batch_result(batch_id, file_name)
        except Exception as e:
            self.add_warning(f"MinerU 解析任务失败: {e}")
            return self._create_empty_result(file_path, document_id)

        try:
            pages, metadata = self._download_and_parse(result_info)
        except Exception as e:
            self.add_warning(f"下载/解析 MinerU 结果失败: {e}")
            return self._create_empty_result(file_path, document_id)

        title = self._extract_title(pages, file_path)

        return ParseResult(
            document_id=document_id,
            title=title,
            source_path=str(file_path),
            file_type="pdf",
            pages=pages,
            metadata=metadata,
            warnings=self.warnings,
        )

    # ---------- MinerU 上传与任务管理 ----------

    def _upload_file(self, file_path: Path):
        """申请上传链接并上传本地 PDF 文件，返回 (batch_id, file_name)"""
        file_name = file_path.name
        req_body = {
            "enable_formula": True,
            "enable_table": True,
            "model_version": self.model_version,
            "files": [{"name": file_name, "is_ocr": True, "data_id": file_name}],
        }
        resp = requests.post(
            f"{self.MINERU_BASE_URL}/file-urls/batch",
            headers=self.headers,
            json=req_body,
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("code") != 0:
            raise RuntimeError(f"申请上传链接失败: {result}")

        batch_id = result["data"]["batch_id"]
        upload_urls = result["data"]["file_urls"]

        with open(file_path, "rb") as f:
            put_resp = requests.put(upload_urls[0], data=f, timeout=120)
            put_resp.raise_for_status()

        return batch_id, file_name

    def _poll_batch_result(self, batch_id: str, file_name: str) -> Dict[str, Any]:
        """轮询批处理任务状态，直到完成或超时"""
        elapsed = 0.0
        url = f"{self.MINERU_BASE_URL}/extract-results/batch/{batch_id}"

        while elapsed < self.poll_timeout:
            resp = requests.get(url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            if result.get("code") != 0:
                raise RuntimeError(f"查询任务状态失败: {result}")

            extract_results = result["data"]["extract_result"]
            for item in extract_results:
                if item.get("file_name") == file_name:
                    state = item.get("state")
                    if state == "done":
                        return item
                    if state == "failed":
                        raise RuntimeError(f"MinerU 解析失败: {item.get('err_msg')}")
                    break  # pending / running，继续等待

            time.sleep(self.poll_interval)
            elapsed += self.poll_interval

        raise TimeoutError("等待 MinerU 解析结果超时")

    # ---------- 结果下载与转换 ----------

    def _download_and_parse(self, result_info: Dict[str, Any]):
        """下载 MinerU 结果 zip 并转换为 PageInfo 列表"""
        zip_url = result_info["full_zip_url"]
        resp = requests.get(zip_url, timeout=60)
        resp.raise_for_status()

        pages: List[PageInfo] = []
        metadata: Dict[str, Any] = {}

        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            names = zf.namelist()

            content_list_name = next(
                (n for n in names if n.endswith("content_list.json")), None
            )
            if content_list_name:
                content_list = json.loads(zf.read(content_list_name).decode("utf-8"))
                pages = self._build_pages_from_content_list(content_list)
                metadata["page_count"] = len(
                    {item.get("page_idx", 0) for item in content_list}
                )
            else:
                # 回退：找不到 content_list.json 时，用整篇 markdown 作为单页文本
                md_name = next((n for n in names if n.endswith(".md")), None)
                if md_name:
                    text = zf.read(md_name).decode("utf-8")
                    pages = [PageInfo(page_number=1, text=text, images=[], tables=[])]
                    metadata["page_count"] = 1
                else:
                    self.add_warning("MinerU 结果中未找到 content_list.json 或 markdown 文件")

        return pages, metadata

    def _build_pages_from_content_list(self, content_list: List[Dict]) -> List[PageInfo]:
        """将 MinerU content_list.json 转换为按页组织的 PageInfo 列表"""
        pages_map: Dict[int, Dict[str, List]] = {}

        for item in content_list:
            page_idx = item.get("page_idx", 0)
            page_entry = pages_map.setdefault(
                page_idx, {"text": [], "images": [], "tables": []}
            )

            item_type = item.get("type")
            if item_type == "text":
                page_entry["text"].append(item.get("text", ""))
            elif item_type == "image":
                page_entry["images"].append(
                    {
                        "path": item.get("img_path", ""),
                        "caption": "".join(item.get("image_caption", [])),
                    }
                )
            elif item_type == "table":
                page_entry["tables"].append(
                    {
                        "html": item.get("table_body", ""),
                        "caption": "".join(item.get("table_caption", [])),
                    }
                )
            else:
                # 公式等其他类型统一并入正文文本
                text_val = item.get("text", "")
                if text_val:
                    page_entry["text"].append(text_val)

        pages = []
        for page_idx in sorted(pages_map.keys()):
            entry = pages_map[page_idx]
            pages.append(
                PageInfo(
                    page_number=page_idx + 1,
                    text="\n".join(entry["text"]),
                    images=entry["images"],
                    tables=entry["tables"],
                )
            )
        return pages

    def _extract_title(self, pages: List[PageInfo], file_path: Path) -> str:
        """从解析结果中提取标题"""
        if pages and pages[0].text.strip():
            first_line = pages[0].text.strip().split("\n")[0].strip().lstrip("#").strip()
            if first_line:
                return first_line[:100]
        return file_path.stem

    def _create_empty_result(self, file_path: Path, document_id: str) -> ParseResult:
        """创建空结果"""
        return ParseResult(
            document_id=document_id,
            title=file_path.stem,
            source_path=str(file_path),
            file_type="pdf",
            pages=[],
            metadata=self.get_metadata(file_path),
            warnings=self.warnings,
        )
