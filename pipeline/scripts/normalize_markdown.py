#!/usr/bin/env python3
"""
Markdown 标准化脚本
将解析结果转换为标准 Markdown 格式
"""

import json
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
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


def load_config(config_path: Path) -> Dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def detect_header_footer(pages: List[Dict], threshold: float = 0.3, min_pages: int = 5) -> List[Dict]:
    """
    检测页眉页脚
    同一文本在超过 threshold 比例的页面出现时，标记为疑似页眉页脚
    """
    if len(pages) < min_pages:
        return []
    
    # 统计每页开头和结尾的文本
    header_candidates = {}  # text -> count
    footer_candidates = {}  # text -> count
    
    for page in pages:
        text = page.get('text', '').strip()
        if not text:
            continue
        
        lines = text.split('\n')
        
        # 检查开头（页眉）
        if len(lines) >= 1:
            header = lines[0].strip()
            if header and len(header) < 100:  # 页眉通常较短
                header_candidates[header] = header_candidates.get(header, 0) + 1
        
        # 检查结尾（页脚）
        if len(lines) >= 2:
            footer = lines[-1].strip()
            if footer and len(footer) < 100:  # 页脚通常较短
                footer_candidates[footer] = footer_candidates.get(footer, 0) + 1
    
    # 找出高频出现的文本
    removals = []
    total_pages = len(pages)
    
    for text, count in header_candidates.items():
        if count / total_pages >= threshold:
            removals.append({
                'type': 'header',
                'text': text,
                'count': count,
                'ratio': count / total_pages,
                'confidence': 'high' if count / total_pages > 0.5 else 'medium'
            })
    
    for text, count in footer_candidates.items():
        if count / total_pages >= threshold:
            removals.append({
                'type': 'footer',
                'text': text,
                'count': count,
                'ratio': count / total_pages,
                'confidence': 'high' if count / total_pages > 0.5 else 'medium'
            })
    
    return removals


def detect_orphan_page_numbers(text: str, patterns: List[str]) -> bool:
    """检测孤立页码"""
    text = text.strip()
    if not text:
        return False
    
    for pattern in patterns:
        if re.match(pattern, text):
            return True
    
    return False


def restore_heading_levels(text: str, heading_patterns: Dict) -> Tuple[str, int]:
    """
    恢复标题层级
    返回: (格式化后的文本, 标题层级)
    """
    text = text.strip()
    if not text:
        return text, 0
    
    # 检查是否匹配标题模式
    for level_name, patterns in heading_patterns.items():
        level = int(level_name.split('_')[1])
        for pattern in patterns:
            if re.match(pattern, text):
                # 添加 Markdown 标题标记
                return f"{'#' * level} {text}", level
    
    return text, 0


def normalize_whitespace(text: str, config: Dict) -> str:
    """标准化空白字符"""
    if not text:
        return text
    
    # 修复多余空格（保留代码块中的空格）
    if config.get('spaces', {}).get('fix_multiple_spaces', True):
        # 不在代码块中时修复空格
        # 简单处理：替换连续空格为单个空格
        text = re.sub(r'(?<!`)  +(?!`)', ' ', text)
    
    # 修复多余空行
    max_blank = config.get('blank_lines', {}).get('max_consecutive', 3)
    replace_with = config.get('blank_lines', {}).get('replace_with', 2)
    pattern = r'\n{' + str(max_blank + 1) + r',}'
    replacement = '\n' * replace_with
    text = re.sub(pattern, replacement, text)
    
    return text


def normalize_punctuation(text: str, config: Dict) -> str:
    """标准化标点符号"""
    if not text:
        return text
    
    # 修复省略号
    if config.get('punctuation', {}).get('fix_ellipsis', True):
        text = re.sub(r'\.{3,}', '……', text)
        text = re.sub(r'…{2,}', '……', text)
    
    return text


def remove_page_numbers(text: str, patterns: List[str]) -> str:
    """移除孤立页码"""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        if not detect_orphan_page_numbers(line, patterns):
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def normalize_page_content(page: Dict, config: Dict, header_footer_removals: List[Dict]) -> Dict:
    """标准化单页内容"""
    text = page.get('text', '')
    
    if not text:
        return page
    
    # 移除页眉页脚
    lines = text.split('\n')
    for removal in header_footer_removals:
        if removal['confidence'] == 'high':
            if removal['type'] == 'header' and lines and lines[0].strip() == removal['text']:
                lines = lines[1:]
            elif removal['type'] == 'footer' and lines and lines[-1].strip() == removal['text']:
                lines = lines[:-1]
    
    text = '\n'.join(lines)
    
    # 移除孤立页码
    if config.get('orphan_page_numbers', {}).get('remove', True):
        patterns = config.get('orphan_page_numbers', {}).get('patterns', [])
        text = remove_page_numbers(text, patterns)
    
    # 标准化空白
    text = normalize_whitespace(text, config)
    
    # 标准化标点
    text = normalize_punctuation(text, config)
    
    # 恢复标题层级
    heading_patterns = config.get('headings', {}).get('patterns', {})
    if heading_patterns and config.get('headings', {}).get('restore_levels', True):
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            formatted_line, _ = restore_heading_levels(line, heading_patterns)
            new_lines.append(formatted_line)
        text = '\n'.join(new_lines)
    
    return {
        **page,
        'text': text
    }


def create_page_map(pages: List[Dict]) -> List[Dict]:
    """创建页码映射"""
    page_map = []
    current_line = 1
    
    for page in pages:
        text = page.get('text', '')
        lines = text.split('\n')
        line_count = len(lines)
        
        page_map.append({
            'page_number': page.get('page_number', 0),
            'start_line': current_line,
            'end_line': current_line + line_count - 1,
            'char_count': len(text)
        })
        
        current_line += line_count
    
    return page_map


def normalize_document(parsed_data: Dict, config: Dict) -> Tuple[str, Dict, List[Dict]]:
    """
    标准化整个文档
    返回: (markdown内容, 元数据, 页码映射)
    """
    pages = parsed_data.get('pages', [])
    normalization_config = config.get('normalization', {})
    
    # 检测页眉页脚
    header_footer_removals = detect_header_footer(
        pages,
        threshold=normalization_config.get('header_footer', {}).get('threshold', 0.3),
        min_pages=normalization_config.get('header_footer', {}).get('min_pages', 5)
    )
    
    # 标准化每页内容
    normalized_pages = []
    for page in pages:
        normalized_page = normalize_page_content(page, normalization_config, header_footer_removals)
        normalized_pages.append(normalized_page)
    
    # 合并为完整 Markdown
    markdown_parts = []
    for page in normalized_pages:
        text = page.get('text', '').strip()
        if text:
            markdown_parts.append(text)
    
    markdown_content = '\n\n'.join(markdown_parts)
    
    # 确保文件末尾有换行符
    if normalization_config.get('output', {}).get('ensure_final_newline', True):
        if not markdown_content.endswith('\n'):
            markdown_content += '\n'
    
    # 创建页码映射
    page_map = create_page_map(normalized_pages)
    
    # 创建元数据
    metadata = {
        'document_id': parsed_data.get('document_id', ''),
        'title': parsed_data.get('title', ''),
        'source_path': parsed_data.get('source_path', ''),
        'file_type': parsed_data.get('file_type', ''),
        'page_count': len(pages),
        'normalized_page_count': len(normalized_pages),
        'total_characters': len(markdown_content),
        'header_footer_removals': len(header_footer_removals),
        'warnings': parsed_data.get('warnings', [])
    }
    
    return markdown_content, metadata, page_map, header_footer_removals


def process_single_document(extracted_dir: Path, output_dir: Path, config: Dict, document_id: str = None, force: bool = False) -> Dict:
    """处理单个文档"""
    logger = logging.getLogger(__name__)
    
    # 查找所有解析结果
    if document_id:
        doc_dirs = [extracted_dir / document_id]
    else:
        doc_dirs = [d for d in extracted_dir.iterdir() if d.is_dir()]
    
    results = {
        'success': 0,
        'skipped': 0,
        'error': 0
    }
    
    for doc_dir in doc_dirs:
        parsed_file = doc_dir / 'parsed.json'
        
        if not parsed_file.exists():
            logger.warning(f"跳过目录 {doc_dir.name}: 未找到 parsed.json")
            results['skipped'] += 1
            continue
        
        # 检查输出是否已存在
        normalized_dir = output_dir / doc_dir.name
        markdown_file = normalized_dir / 'document.md'
        
        if markdown_file.exists() and not force:
            logger.info(f"跳过已标准化文档: {doc_dir.name}")
            results['skipped'] += 1
            continue
        
        try:
            # 加载解析结果
            with open(parsed_file, 'r', encoding='utf-8') as f:
                parsed_data = json.load(f)
            
            logger.info(f"开始标准化: {parsed_data.get('title', doc_dir.name)}")
            
            # 标准化文档
            markdown_content, metadata, page_map, header_footer_removals = normalize_document(parsed_data, config)
            
            # 创建输出目录
            normalized_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存 Markdown
            with open(markdown_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            # 保存元数据
            with open(normalized_dir / 'metadata.json', 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 保存页码映射
            with open(normalized_dir / 'page_map.json', 'w', encoding='utf-8') as f:
                json.dump(page_map, f, ensure_ascii=False, indent=2)
            
            # 保存页眉页脚移除记录
            if header_footer_removals:
                removals_file = output_dir.parent / 'logs' / 'header_footer_removal.jsonl'
                removals_file.parent.mkdir(parents=True, exist_ok=True)
                with open(removals_file, 'a', encoding='utf-8') as f:
                    for removal in header_footer_removals:
                        removal['document_id'] = doc_dir.name
                        f.write(json.dumps(removal, ensure_ascii=False) + '\n')
            
            logger.info(f"标准化完成: {metadata['title']}, 字符数: {metadata['total_characters']}")
            results['success'] += 1
            
        except Exception as e:
            logger.error(f"标准化文档 {doc_dir.name} 时出错: {e}")
            results['error'] += 1
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Markdown 标准化脚本")
    parser.add_argument("--extracted-dir", required=True, help="解析结果目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--config", required=True, help="配置文件路径")
    parser.add_argument("--log-file", help="日志文件路径")
    parser.add_argument("--document-id", help="只处理指定文档ID")
    parser.add_argument("--force", action="store_true", help="强制重新处理")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_file)
    logger = logging.getLogger(__name__)
    
    # 加载配置
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"配置文件不存在: {config_path}")
        return
    
    config = load_config(config_path)
    
    # 检查目录
    extracted_dir = Path(args.extracted_dir)
    output_dir = Path(args.output_dir)
    
    if not extracted_dir.exists():
        logger.error(f"解析结果目录不存在: {extracted_dir}")
        return
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("开始 Markdown 标准化")
    
    # 处理文档
    results = process_single_document(extracted_dir, output_dir, config, args.document_id, args.force)
    
    # 输出统计
    logger.info("标准化完成!")
    logger.info(f"成功: {results['success']}")
    logger.info(f"跳过: {results['skipped']}")
    logger.info(f"错误: {results['error']}")


if __name__ == "__main__":
    main()
