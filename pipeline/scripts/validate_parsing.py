#!/usr/bin/env python3
"""
解析质量验证脚本
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Set
from tqdm import tqdm


def load_parsed_results(extracted_dir: Path) -> List[Dict]:
    """加载所有解析结果"""
    results = []
    
    for doc_dir in extracted_dir.iterdir():
        if doc_dir.is_dir():
            parsed_file = doc_dir / 'parsed.json'
            report_file = doc_dir / 'parse_report.json'
            
            if parsed_file.exists() and report_file.exists():
                with open(parsed_file, 'r', encoding='utf-8') as f:
                    parsed_data = json.load(f)
                
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                results.append({
                    'document_id': doc_dir.name,
                    'parsed': parsed_data,
                    'report': report_data
                })
    
    return results


def validate_document(doc_data: Dict) -> List[str]:
    """验证单个文档"""
    issues = []
    
    parsed = doc_data['parsed']
    report = doc_data['report']
    
    # 检查基本字段
    required_fields = ['document_id', 'title', 'source_path', 'file_type', 'pages']
    for field in required_fields:
        if field not in parsed:
            issues.append(f"缺少必要字段: {field}")
    
    # 检查页面
    pages = parsed.get('pages', [])
    if not pages:
        issues.append("文档没有页面内容")
    
    # 检查每页内容
    empty_pages = []
    short_pages = []
    
    for page in pages:
        page_num = page.get('page_number', 0)
        text = page.get('text', '')
        
        if not text.strip():
            empty_pages.append(page_num)
        elif len(text.strip()) < 10:
            short_pages.append(page_num)
    
    if empty_pages:
        issues.append(f"有 {len(empty_pages)} 个空页面: {empty_pages[:5]}...")
    
    if short_pages:
        issues.append(f"有 {len(short_pages)} 个内容过短的页面: {short_pages[:5]}...")
    
    # 检查标题
    title = parsed.get('title', '')
    if not title or title == Path(parsed.get('source_path', '')).stem:
        issues.append("标题可能是文件名，未正确提取")
    
    # 检查警告
    warnings = report.get('warnings', [])
    if warnings:
        issues.append(f"有 {len(warnings)} 个警告: {warnings[:3]}...")
    
    # 检查解析状态
    parse_status = report.get('parse_status', '')
    if parse_status != 'success':
        issues.append(f"解析状态异常: {parse_status}")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description="解析质量验证")
    parser.add_argument("--extracted-dir", required=True, help="解析结果目录")
    parser.add_argument("--output", help="输出验证报告文件路径")
    
    args = parser.parse_args()
    
    extracted_dir = Path(args.extracted_dir)
    if not extracted_dir.exists():
        print(f"错误: 解析结果目录不存在: {extracted_dir}")
        return
    
    # 加载解析结果
    print("加载解析结果...")
    results = load_parsed_results(extracted_dir)
    print(f"找到 {len(results)} 个已解析文档")
    
    # 验证每个文档
    validation_results = []
    
    print("\n验证文档质量...")
    for doc_data in tqdm(results, desc="验证文档"):
        issues = validate_document(doc_data)
        
        validation_results.append({
            'document_id': doc_data['document_id'],
            'title': doc_data['parsed'].get('title', ''),
            'file_type': doc_data['parsed'].get('file_type', ''),
            'page_count': len(doc_data['parsed'].get('pages', [])),
            'character_count': doc_data['report'].get('character_count', 0),
            'issue_count': len(issues),
            'issues': issues,
            'status': 'pass' if not issues else 'fail'
        })
    
    # 统计结果
    pass_count = sum(1 for r in validation_results if r['status'] == 'pass')
    fail_count = sum(1 for r in validation_results if r['status'] == 'fail')
    
    print(f"\n验证完成!")
    print(f"通过: {pass_count}")
    print(f"失败: {fail_count}")
    print(f"通过率: {pass_count / len(validation_results) * 100:.1f}%")
    
    # 显示失败文档
    if fail_count > 0:
        print(f"\n失败文档:")
        for result in validation_results:
            if result['status'] == 'fail':
                print(f"\n文档: {result['title']}")
                print(f"ID: {result['document_id']}")
                print(f"类型: {result['file_type']}")
                print(f"页数: {result['page_count']}")
                print(f"问题:")
                for issue in result['issues']:
                    print(f"  - {issue}")
    
    # 保存验证报告
    if args.output:
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_documents': len(validation_results),
                'pass_count': pass_count,
                'fail_count': fail_count,
                'pass_rate': pass_count / len(validation_results) * 100,
                'results': validation_results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n验证报告已保存: {output_file}")


if __name__ == "__main__":
    main()