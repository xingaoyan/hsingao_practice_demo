#!/usr/bin/env python3
"""
Markdown 校验器
检查标准化后的 Markdown 文件质量
"""

import json
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional
from tqdm import tqdm


def setup_logging(log_file: Optional[str] = None):
    """设置日志"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if log_file:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format
        )


def check_empty_document(content: str) -> List[str]:
    """检查空文档"""
    issues = []
    
    if not content or not content.strip():
        issues.append("文档内容为空")
    elif len(content.strip()) < 100:
        issues.append(f"文档内容过短 ({len(content.strip())} 字符)")
    
    return issues


def check_heading_levels(content: str) -> List[str]:
    """检查标题层级跳跃"""
    issues = []
    
    if not content:
        return issues
    
    lines = content.split('\n')
    prev_level = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # 检查是否为标题
        match = re.match(r'^(#{1,6})\s', line)
        if match:
            level = len(match.group(1))
            
            # 检查层级跳跃（例如从 # 直接到 ###）
            if prev_level > 0 and level > prev_level + 1:
                issues.append(f"第 {i+1} 行: 标题层级跳跃 (从 {prev_level} 级跳到 {level} 级)")
            
            prev_level = level
    
    return issues


def check_unclosed_code_blocks(content: str) -> List[str]:
    """检查未闭合的代码块"""
    issues = []
    
    if not content:
        return issues
    
    # 计算代码块标记数量
    triple_backticks = content.count('```')
    
    if triple_backticks % 2 != 0:
        issues.append(f"代码块未闭合 (找到 {triple_backticks} 个 ``` 标记)")
    
    return issues


def check_unclosed_tables(content: str) -> List[str]:
    """检查未闭合的表格"""
    issues = []
    
    if not content:
        return issues
    
    lines = content.split('\n')
    in_table = False
    table_start_line = 0
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith('|') and '|' in line[1:]:
            if not in_table:
                in_table = True
                table_start_line = i + 1
        elif in_table and not line.startswith('|'):
            # 表格结束，检查是否有分隔行
            in_table = False
    
    if in_table:
        issues.append(f"表格未闭合 (从第 {table_start_line} 行开始)")
    
    return issues


def check_image_references(content: str) -> List[str]:
    """检查图片引用"""
    issues = []
    
    if not content:
        return issues
    
    # 查找 Markdown 图片引用
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    matches = re.findall(image_pattern, content)
    
    for alt_text, url in matches:
        if not url:
            issues.append(f"图片引用 URL 为空: ![{alt_text}]()")
    
    return issues


def check_duplicate_content(content: str, threshold: int = 100) -> List[str]:
    """检查大段重复内容"""
    issues = []
    
    if not content:
        return issues
    
    lines = content.split('\n')
    
    # 检查连续重复行
    consecutive_count = 1
    prev_line = None
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        if line == prev_line:
            consecutive_count += 1
        else:
            if consecutive_count >= 3:
                issues.append(f"第 {i - consecutive_count + 1}-{i} 行: 连续重复 {consecutive_count} 次")
            consecutive_count = 1
        
        prev_line = line
    
    return issues


def check_page_mapping(normalized_dir: Path) -> List[str]:
    """检查页码映射"""
    issues = []
    
    page_map_file = normalized_dir / 'page_map.json'
    metadata_file = normalized_dir / 'metadata.json'
    
    if not page_map_file.exists():
        issues.append("缺少页码映射文件 (page_map.json)")
        return issues
    
    if not metadata_file.exists():
        issues.append("缺少元数据文件 (metadata.json)")
        return issues
    
    try:
        with open(page_map_file, 'r', encoding='utf-8') as f:
            page_map = json.load(f)
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # 检查页码映射是否为空
        if not page_map:
            issues.append("页码映射为空")
        
        # 检查页码是否连续
        expected_pages = list(range(1, metadata.get('page_count', 0) + 1))
        actual_pages = [p.get('page_number', 0) for p in page_map]
        
        missing_pages = set(expected_pages) - set(actual_pages)
        if missing_pages:
            issues.append(f"缺少页码映射: {sorted(missing_pages)[:5]}...")
        
    except Exception as e:
        issues.append(f"读取页码映射失败: {e}")
    
    return issues


def validate_markdown_file(markdown_file: Path, normalized_dir: Path = None) -> Dict:
    """验证单个 Markdown 文件"""
    issues = []
    
    try:
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查空文档
        issues.extend(check_empty_document(content))
        
        # 检查标题层级
        issues.extend(check_heading_levels(content))
        
        # 检查未闭合代码块
        issues.extend(check_unclosed_code_blocks(content))
        
        # 检查未闭合表格
        issues.extend(check_unclosed_tables(content))
        
        # 检查图片引用
        issues.extend(check_image_references(content))
        
        # 检查重复内容
        issues.extend(check_duplicate_content(content))
        
        # 检查页码映射
        if normalized_dir:
            issues.extend(check_page_mapping(normalized_dir))
        
        # 统计信息
        lines = content.split('\n')
        stats = {
            'total_lines': len(lines),
            'total_chars': len(content),
            'heading_count': sum(1 for line in lines if re.match(r'^#{1,6}\s', line.strip())),
            'code_block_count': content.count('```') // 2,
            'table_count': sum(1 for line in lines if line.strip().startswith('|'))
        }
        
    except Exception as e:
        issues.append(f"读取文件失败: {e}")
        stats = {}
    
    return {
        'file': str(markdown_file),
        'issues': issues,
        'issue_count': len(issues),
        'stats': stats,
        'status': 'pass' if not issues else 'fail'
    }


def main():
    parser = argparse.ArgumentParser(description="Markdown 校验器")
    parser.add_argument("--normalized-dir", required=True, help="标准化输出目录")
    parser.add_argument("--output", help="输出校验报告文件路径")
    parser.add_argument("--log-file", help="日志文件路径")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_file)
    logger = logging.getLogger(__name__)
    
    normalized_dir = Path(args.normalized_dir)
    if not normalized_dir.exists():
        logger.error(f"标准化目录不存在: {normalized_dir}")
        return
    
    # 查找所有 Markdown 文件
    markdown_files = list(normalized_dir.rglob('document.md'))
    
    if not markdown_files:
        logger.warning(f"未找到 Markdown 文件: {normalized_dir}")
        return
    
    logger.info(f"找到 {len(markdown_files)} 个 Markdown 文件")
    
    # 验证每个文件
    results = []
    
    for markdown_file in tqdm(markdown_files, desc="校验 Markdown"):
        doc_dir = markdown_file.parent
        result = validate_markdown_file(markdown_file, doc_dir)
        results.append(result)
    
    # 统计结果
    pass_count = sum(1 for r in results if r['status'] == 'pass')
    fail_count = sum(1 for r in results if r['status'] == 'fail')
    
    logger.info(f"\n校验完成!")
    logger.info(f"通过: {pass_count}")
    logger.info(f"失败: {fail_count}")
    
    if fail_count > 0:
        logger.info(f"\n失败文件:")
        for result in results:
            if result['status'] == 'fail':
                logger.info(f"\n文件: {result['file']}")
                for issue in result['issues']:
                    logger.info(f"  - {issue}")
    
    # 保存校验报告
    if args.output:
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'total_files': len(results),
            'pass_count': pass_count,
            'fail_count': fail_count,
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n校验报告已保存: {output_file}")


if __name__ == "__main__":
    main()
