#!/usr/bin/env python3
"""
解析器测试脚本
"""

import json
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'pipeline'))

from parsers import PDFParser, DOCXParser, TextParser


def test_pdf_parser():
    """测试 PDF 解析器"""
    print("测试 PDF 解析器...")
    
    # 查找一个 PDF 文件
    manifest_file = Path(__file__).parent.parent / 'data' / 'manifest' / 'materials_manifest.jsonl'
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                file_info = json.loads(line)
                if file_info['file_type'] == 'pdf':
                    print(f"  测试文件: {file_info['filename']}")
                    
                    parser = PDFParser()
                    result = parser.parse(
                        Path(file_info['absolute_path']),
                        file_info['file_id']
                    )
                    
                    print(f"    标题: {result.title}")
                    print(f"    页数: {len(result.pages)}")
                    print(f"    字符数: {sum(len(page.text) for page in result.pages)}")
                    print(f"    警告: {len(result.warnings)}")
                    
                    if result.pages:
                        print(f"    第一页内容预览: {result.pages[0].text[:100]}...")
                    
                    print("    ✓ PDF 解析器测试通过")
                    return True
    
    print("    ✗ 未找到 PDF 文件")
    return False


def test_docx_parser():
    """测试 DOCX 解析器"""
    print("测试 DOCX 解析器...")
    
    # 查找一个 DOCX 文件
    manifest_file = Path(__file__).parent.parent / 'data' / 'manifest' / 'materials_manifest.jsonl'
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                file_info = json.loads(line)
                if file_info['file_type'] == 'docx':
                    print(f"  测试文件: {file_info['filename']}")
                    
                    parser = DOCXParser()
                    result = parser.parse(
                        Path(file_info['absolute_path']),
                        file_info['file_id']
                    )
                    
                    print(f"    标题: {result.title}")
                    print(f"    页数: {len(result.pages)}")
                    print(f"    字符数: {sum(len(page.text) for page in result.pages)}")
                    print(f"    警告: {len(result.warnings)}")
                    
                    if result.pages:
                        print(f"    第一页内容预览: {result.pages[0].text[:100]}...")
                    
                    print("    ✓ DOCX 解析器测试通过")
                    return True
    
    print("    ✗ 未找到 DOCX 文件")
    return False


def test_text_parser():
    """测试文本解析器"""
    print("测试文本解析器...")
    
    # 创建一个临时 Markdown 文件
    test_content = """# 测试标题

这是一个测试文档。

## 第一节

这是第一节的内容。

## 第二节

这是第二节的内容。
"""
    
    test_file = Path(__file__).parent / 'test.md'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        parser = TextParser()
        result = parser.parse(test_file, 'test-doc-id')
        
        print(f"    标题: {result.title}")
        print(f"    页数: {len(result.pages)}")
        print(f"    字符数: {sum(len(page.text) for page in result.pages)}")
        print(f"    警告: {len(result.warnings)}")
        
        if result.pages:
            print(f"    第一页内容预览: {result.pages[0].text[:100]}...")
        
        print("    ✓ 文本解析器测试通过")
        return True
        
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()


def main():
    print("开始解析器测试...\n")
    
    tests = [
        test_pdf_parser,
        test_docx_parser,
        test_text_parser,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"    ✗ 测试失败: {e}")
            failed += 1
        print()
    
    print(f"测试结果: {passed} 通过, {failed} 失败")
    
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()