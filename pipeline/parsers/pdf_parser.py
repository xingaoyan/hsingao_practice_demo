#!/usr/bin/env python3
"""
PDF 解析器
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
import pymupdf

from .base import BaseParser, ParseResult, PageInfo


class PDFParser(BaseParser):
    """PDF 解析器"""
    
    def __init__(self):
        super().__init__()
        self.min_text_chars = 30  # 扫描页判断阈值
    
    def parse(self, file_path: Path, document_id: str) -> ParseResult:
        """解析 PDF 文件"""
        self.clear_warnings()
        
        try:
            doc = pymupdf.open(str(file_path))
        except Exception as e:
            self.add_warning(f"无法打开 PDF 文件: {e}")
            return self._create_empty_result(file_path, document_id)
        
        pages = []
        metadata = self._extract_metadata(doc)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_info = self._parse_page(page, page_num + 1)
            pages.append(page_info)
        
        # 提取标题
        title = self._extract_title(doc, file_path)
        
        doc.close()
        
        return ParseResult(
            document_id=document_id,
            title=title,
            source_path=str(file_path),
            file_type="pdf",
            pages=pages,
            metadata=metadata,
            warnings=self.warnings
        )
    
    def _parse_page(self, page, page_number: int) -> PageInfo:
        """解析单页"""
        try:
            # 提取文本
            text = page.get_text()
            
            # 检查是否为扫描页
            is_scan_page = self._is_scan_page(page, text)
            
            if is_scan_page:
                self.add_warning(f"第 {page_number} 页可能是扫描页，文本内容较少")
            
            # 提取图片信息
            images = self._extract_images(page)
            
            # 提取表格信息
            tables = self._extract_tables(page)
            
            return PageInfo(
                page_number=page_number,
                text=text,
                images=images,
                tables=tables
            )
            
        except Exception as e:
            self.add_warning(f"解析第 {page_number} 页时出错: {e}")
            return PageInfo(
                page_number=page_number,
                text="",
                images=[],
                tables=[]
            )
    
    def _is_scan_page(self, page, text: str) -> bool:
        """判断是否为扫描页"""
        # 文本少于阈值字符
        if len(text.strip()) < self.min_text_chars:
            # 检查是否有大尺寸图片
            images = page.get_images()
            if images:
                for img in images:
                    xref = img[0]
                    try:
                        image = page.parent.extract_image(xref)
                        if image:
                            width, height = image.get("width", 0), image.get("height", 0)
                            # 如果图片尺寸较大，认为是扫描页
                            if width > 500 or height > 500:
                                return True
                    except:
                        pass
        return False
    
    def _extract_images(self, page) -> List[Dict]:
        """提取页面图片信息"""
        images = []
        try:
            image_list = page.get_images()
            for img in image_list:
                xref = img[0]
                images.append({
                    "xref": xref,
                    "width": img[2] if len(img) > 2 else None,
                    "height": img[3] if len(img) > 3 else None
                })
        except Exception as e:
            self.add_warning(f"提取图片信息时出错: {e}")
        return images
    
    def _extract_tables(self, page) -> List[Dict]:
        """提取页面表格信息"""
        tables = []
        try:
            # PyMuPDF 的表格提取功能
            table_finder = page.find_tables()
            for i, table in enumerate(table_finder.tables):
                tables.append({
                    "index": i,
                    "rows": table.rows,
                    "columns": table.cols,
                    "bbox": table.bbox
                })
        except Exception as e:
            # 表格提取可能失败，这不是致命错误
            pass
        return tables
    
    def _extract_metadata(self, doc) -> Dict[str, Any]:
        """提取 PDF 元数据"""
        metadata = {}
        try:
            pdf_metadata = doc.metadata
            if pdf_metadata:
                metadata.update({
                    "title": pdf_metadata.get("title", ""),
                    "author": pdf_metadata.get("author", ""),
                    "subject": pdf_metadata.get("subject", ""),
                    "creator": pdf_metadata.get("creator", ""),
                    "producer": pdf_metadata.get("producer", ""),
                    "creation_date": pdf_metadata.get("creationDate", ""),
                    "modification_date": pdf_metadata.get("modDate", "")
                })
            
            metadata["page_count"] = len(doc)
            
        except Exception as e:
            self.add_warning(f"提取元数据时出错: {e}")
        
        return metadata
    
    def _extract_title(self, doc, file_path: Path) -> str:
        """提取文档标题"""
        # 首先尝试从元数据获取
        try:
            pdf_metadata = doc.metadata
            if pdf_metadata and pdf_metadata.get("title"):
                return pdf_metadata["title"]
        except:
            pass
        
        # 尝试从第一页提取
        try:
            if len(doc) > 0:
                first_page = doc[0]
                text = first_page.get_text()
                # 取第一行作为标题
                lines = text.strip().split('\n')
                if lines:
                    return lines[0].strip()[:100]  # 限制标题长度
        except:
            pass
        
        # 使用文件名作为标题
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
            warnings=self.warnings
        )