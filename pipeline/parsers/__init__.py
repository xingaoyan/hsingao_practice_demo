#!/usr/bin/env python3
"""
解析器模块
"""

from .base import BaseParser, ParseResult, PageInfo
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .pptx_parser import PPTXParser
from .text_parser import TextParser
from .excel_parser import ExcelParser

__all__ = [
    'BaseParser',
    'ParseResult',
    'PageInfo',
    'PDFParser',
    'DOCXParser',
    'PPTXParser',
    'TextParser',
    'ExcelParser'
]