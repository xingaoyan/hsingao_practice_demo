#!/usr/bin/env python3
"""
Markdown 和 TXT 解析器
"""

import chardet
from pathlib import Path
from typing import Dict, List, Optional, Any

from .base import BaseParser, ParseResult, PageInfo


class TextParser(BaseParser):
    """Markdown 和 TXT 解析器"""
    
    def parse(self, file_path: Path, document_id: str) -> ParseResult:
        """解析 Markdown 或 TXT 文件"""
        self.clear_warnings()
        
        try:
            # 检测编码
            encoding = self._detect_encoding(file_path)
            
            # 读取文件内容
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # 处理异常换行
            content = self._normalize_line_endings(content)
            
            # 创建页面（将内容分页）
            pages = self._split_into_pages(content, file_path.suffix.lower())
            
            # 提取元数据
            metadata = self._extract_metadata(file_path, content, encoding)
            
            # 提取标题
            title = self._extract_title(content, file_path)
            
            return ParseResult(
                document_id=document_id,
                title=title,
                source_path=str(file_path),
                file_type="markdown" if file_path.suffix.lower() == '.md' else "text",
                pages=pages,
                metadata=metadata,
                warnings=self.warnings
            )
            
        except Exception as e:
            self.add_warning(f"无法读取文件: {e}")
            return self._create_empty_result(file_path, document_id)
    
    def _detect_encoding(self, file_path: Path) -> str:
        """检测文件编码"""
        try:
            # 读取部分文件内容进行编码检测
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
            
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            
            # 如果检测失败，使用 utf-8
            if not encoding:
                encoding = 'utf-8'
            
            return encoding
            
        except Exception as e:
            self.add_warning(f"编码检测失败，使用默认编码 utf-8: {e}")
            return 'utf-8'
    
    def _normalize_line_endings(self, content: str) -> str:
        """标准化换行符"""
        # 统一换行符
        content = content.replace('\r\n', '\n')
        content = content.replace('\r', '\n')
        return content
    
    def _split_into_pages(self, content: str, file_extension: str) -> List[PageInfo]:
        """将内容分页"""
        pages = []
        
        if file_extension == '.md':
            # Markdown 文件按标题分页
            pages = self._split_markdown_by_headings(content)
        else:
            # TXT 文件按固定行数分页
            pages = self._split_text_by_lines(content)
        
        # 如果没有分页，创建单页
        if not pages:
            pages = [PageInfo(page_number=1, text=content)]
        
        return pages
    
    def _split_markdown_by_headings(self, content: str) -> List[PageInfo]:
        """按 Markdown 标题分页"""
        pages = []
        current_page = []
        page_number = 1
        
        lines = content.split('\n')
        
        for line in lines:
            # 检查是否为标题行
            if line.startswith('#') and len(line) > 1:
                # 如果当前页有内容，保存
                if current_page:
                    pages.append(PageInfo(
                        page_number=page_number,
                        text='\n'.join(current_page)
                    ))
                    page_number += 1
                    current_page = []
            
            current_page.append(line)
        
        # 保存最后一页
        if current_page:
            pages.append(PageInfo(
                page_number=page_number,
                text='\n'.join(current_page)
            ))
        
        return pages
    
    def _split_text_by_lines(self, content: str, lines_per_page: int = 50) -> List[PageInfo]:
        """按行数分页"""
        pages = []
        lines = content.split('\n')
        
        for i in range(0, len(lines), lines_per_page):
            page_lines = lines[i:i + lines_per_page]
            pages.append(PageInfo(
                page_number=i // lines_per_page + 1,
                text='\n'.join(page_lines)
            ))
        
        return pages
    
    def _extract_metadata(self, file_path: Path, content: str, encoding: str) -> Dict[str, Any]:
        """提取文件元数据"""
        metadata = self.get_metadata(file_path)
        metadata["encoding"] = encoding
        
        # 统计信息
        lines = content.split('\n')
        metadata["line_count"] = len(lines)
        metadata["character_count"] = len(content)
        
        # 如果是 Markdown，统计标题数量
        if file_path.suffix.lower() == '.md':
            heading_count = sum(1 for line in lines if line.startswith('#'))
            metadata["heading_count"] = heading_count
        
        return metadata
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """提取文档标题"""
        lines = content.split('\n')
        
        # 尝试从第一个标题提取
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                # 去掉 # 符号
                title = line.lstrip('#').strip()
                if title:
                    return title[:100]
        
        # 尝试从第一行非空内容提取
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                return line[:100]
        
        # 使用文件名作为标题
        return file_path.stem
    
    def _create_empty_result(self, file_path: Path, document_id: str) -> ParseResult:
        """创建空结果"""
        return ParseResult(
            document_id=document_id,
            title=file_path.stem,
            source_path=str(file_path),
            file_type="markdown" if file_path.suffix.lower() == '.md' else "text",
            pages=[],
            metadata=self.get_metadata(file_path),
            warnings=self.warnings
        )