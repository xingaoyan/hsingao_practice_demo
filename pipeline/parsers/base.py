#!/usr/bin/env python3
"""
基础解析器定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path


@dataclass
class PageInfo:
    """页面信息"""
    page_number: int
    text: str
    images: List[Dict] = None
    tables: List[Dict] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.tables is None:
            self.tables = []


@dataclass
class ParseResult:
    """解析结果"""
    document_id: str
    title: str
    source_path: str
    file_type: str
    pages: List[PageInfo]
    metadata: Dict[str, Any]
    warnings: List[str]
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "document_id": self.document_id,
            "title": self.title,
            "source_path": self.source_path,
            "file_type": self.file_type,
            "pages": [
                {
                    "page_number": page.page_number,
                    "text": page.text,
                    "images": page.images,
                    "tables": page.tables
                }
                for page in self.pages
            ],
            "metadata": self.metadata,
            "warnings": self.warnings
        }


class BaseParser(ABC):
    """基础解析器类"""
    
    def __init__(self):
        self.warnings = []
    
    @abstractmethod
    def parse(self, file_path: Path, document_id: str) -> ParseResult:
        """解析文件"""
        pass
    
    def add_warning(self, message: str):
        """添加警告信息"""
        self.warnings.append(message)
    
    def clear_warnings(self):
        """清除警告信息"""
        self.warnings = []
    
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """获取文件元数据"""
        stat = file_path.stat()
        return {
            "filename": file_path.name,
            "size_bytes": stat.st_size,
            "modified_at": stat.st_mtime,
            "extension": file_path.suffix.lower()
        }