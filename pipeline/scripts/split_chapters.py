#!/usr/bin/env python3
"""
章节切分脚本
将标准化的 Markdown 文档切分为章节
"""

import json
import re
import argparse
import hashlib
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
    """加载课程大纲配置"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_section_id(document_id: str, title: str, index: int) -> str:
    """生成稳定的章节ID"""
    content = f"{document_id}:{title}:{index}"
    hash_value = hashlib.md5(content.encode()).hexdigest()[:12]
    return f"sec_{hash_value}"


def detect_heading_level(line: str) -> Tuple[int, str]:
    """
    检测标题级别
    返回: (级别, 标题文本)
    """
    line = line.strip()
    if not line:
        return 0, ""
    
    # Markdown 标题格式
    match = re.match(r'^(#{1,6})\s+(.+)$', line)
    if match:
        level = len(match.group(1))
        title = match.group(2).strip()
        return level, title
    
    # 中文章节格式
    patterns = [
        (r'^第[一二三四五六七八九十百千\d]+[章篇部]\s*(.*)$', 1),
        (r'^第\d+章\s*(.*)$', 1),
        (r'^Chapter\s+\d+\s*(.*)$', 1),
        (r'^\d+\.\d+\s+(.+)$', 2),
        (r'^第[一二三四五六七八九十]+节\s*(.*)$', 2),
        (r'^Section\s+\d+\s*(.*)$', 2),
        (r'^\d+\.\d+\.\d+\s+(.+)$', 3),
        (r'^\d+\.\d+\.\d+$', 3),
    ]
    
    for pattern, level in patterns:
        match = re.match(pattern, line)
        if match:
            title = match.group(1).strip() if match.group(1) else line
            return level, title
    
    return 0, ""


def split_into_sections(content: str, page_map: List[Dict]) -> List[Dict]:
    """
    将内容切分为章节
    """
    lines = content.split('\n')
    sections = []
    current_section = None
    current_content = []
    current_start_line = 1
    
    for i, line in enumerate(lines, 1):
        level, title = detect_heading_level(line)
        
        if level > 0 and title:
            # 保存之前的章节
            if current_section:
                current_section['content_markdown'] = '\n'.join(current_content).strip()
                current_section['end_line'] = i - 1
                # 计算页码
                current_section['source_page_start'] = get_page_for_line(current_start_line, page_map)
                current_section['source_page_end'] = get_page_for_line(i - 1, page_map)
                sections.append(current_section)
            
            # 开始新章节
            current_section = {
                'title': title,
                'heading_level': level,
                'start_line': i,
                'order_index': len(sections)
            }
            current_content = []
            current_start_line = i
        else:
            current_content.append(line)
    
    # 保存最后一个章节
    if current_section:
        current_section['content_markdown'] = '\n'.join(current_content).strip()
        current_section['end_line'] = len(lines)
        current_section['source_page_start'] = get_page_for_line(current_start_line, page_map)
        current_section['source_page_end'] = get_page_for_line(len(lines), page_map)
        sections.append(current_section)
    
    return sections


def get_page_for_line(line_number: int, page_map: List[Dict]) -> int:
    """根据行号获取页码"""
    for page_info in page_map:
        if page_info['start_line'] <= line_number <= page_info['end_line']:
            return page_info['page_number']
    return 0


def classify_section(title: str, content: str, chapter_keywords: Dict) -> Tuple[Optional[str], float]:
    """
    根据关键词对章节进行分类
    返回: (章节ID, 置信度)
    """
    text = (title + ' ' + content[:500]).lower()
    
    scores = {}
    for chapter_id, keywords in chapter_keywords.items():
        score = 0
        for keyword in keywords:
            if keyword.lower() in text:
                score += 1
        if score > 0:
            scores[chapter_id] = score / len(keywords)
    
    if not scores:
        return None, 0.0
    
    best_chapter = max(scores, key=scores.get)
    return best_chapter, scores[best_chapter]


def process_document(normalized_dir: Path, output_dir: Path, config: Dict, document_id: str = None, force: bool = False) -> Dict:
    """处理单个文档"""
    logger = logging.getLogger(__name__)
    
    # 查找所有标准化文档
    if document_id:
        doc_dirs = [normalized_dir / document_id]
    else:
        doc_dirs = [d for d in normalized_dir.iterdir() if d.is_dir()]
    
    results = {
        'success': 0,
        'skipped': 0,
        'error': 0,
        'total_sections': 0
    }
    
    chapter_keywords = config.get('chapter_keywords', {})
    
    for doc_dir in doc_dirs:
        markdown_file = doc_dir / 'document.md'
        page_map_file = doc_dir / 'page_map.json'
        metadata_file = doc_dir / 'metadata.json'
        
        if not markdown_file.exists():
            logger.warning(f"跳过目录 {doc_dir.name}: 未找到 document.md")
            results['skipped'] += 1
            continue
        
        # 检查输出是否已存在
        output_file = output_dir / doc_dir.name / 'sections.jsonl'
        if output_file.exists() and not force:
            logger.info(f"跳过已切分文档: {doc_dir.name}")
            results['skipped'] += 1
            continue
        
        try:
            # 加载内容
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 加载页码映射
            page_map = []
            if page_map_file.exists():
                with open(page_map_file, 'r', encoding='utf-8') as f:
                    page_map = json.load(f)
            
            # 加载元数据
            metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            logger.info(f"开始切分: {metadata.get('title', doc_dir.name)}")
            
            # 切分章节
            sections = split_into_sections(content, page_map)
            
            # 为每个章节添加ID和分类
            doc_id = metadata.get('document_id', doc_dir.name)
            for i, section in enumerate(sections):
                section['section_id'] = generate_section_id(doc_id, section['title'], i)
                section['document_id'] = doc_id
                
                # 自动分类
                predicted_chapter, confidence = classify_section(
                    section['title'],
                    section['content_markdown'],
                    chapter_keywords
                )
                
                section['predicted_chapter'] = predicted_chapter
                section['classification_confidence'] = confidence
                section['review_status'] = 'pending'
                section['content_type'] = '教材正文'  # 默认类型
            
            # 创建输出目录
            output_dir_doc = output_dir / doc_dir.name
            output_dir_doc.mkdir(parents=True, exist_ok=True)
            
            # 保存章节
            with open(output_file, 'w', encoding='utf-8') as f:
                for section in sections:
                    # 清理不需要保存到JSON的字段
                    save_section = {k: v for k, v in section.items()}
                    f.write(json.dumps(save_section, ensure_ascii=False) + '\n')
            
            logger.info(f"切分完成: {len(sections)} 个章节")
            results['success'] += 1
            results['total_sections'] += len(sections)
            
        except Exception as e:
            logger.error(f"切分文档 {doc_dir.name} 时出错: {e}")
            results['error'] += 1
    
    return results


def create_review_file(output_dir: Path) -> Path:
    """创建人工校验文件"""
    review_file = output_dir / 'section_review.csv'
    
    # 收集所有章节
    all_sections = []
    for doc_dir in output_dir.iterdir():
        if doc_dir.is_dir():
            sections_file = doc_dir / 'sections.jsonl'
            if sections_file.exists():
                with open(sections_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            section = json.loads(line)
                            all_sections.append(section)
    
    # 写入CSV
    with open(review_file, 'w', encoding='utf-8') as f:
        f.write('section_id,document_id,section_title,heading_level,predicted_chapter,confidence,content_type,review_status,review_comment\n')
        for section in all_sections:
            f.write(f"{section.get('section_id', '')},")
            f.write(f"{section.get('document_id', '')},")
            f.write(f"\"{section.get('title', '')}\",")
            f.write(f"{section.get('heading_level', 0)},")
            f.write(f"{section.get('predicted_chapter', '')},")
            f.write(f"{section.get('classification_confidence', 0):.2f},")
            f.write(f"{section.get('content_type', '')},")
            f.write(f"{section.get('review_status', 'pending')},")
            f.write(f"\n")
    
    return review_file


def main():
    parser = argparse.ArgumentParser(description="章节切分脚本")
    parser.add_argument("--normalized-dir", required=True, help="标准化文档目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--config", required=True, help="课程大纲配置文件")
    parser.add_argument("--log-file", help="日志文件路径")
    parser.add_argument("--document-id", help="只处理指定文档ID")
    parser.add_argument("--force", action="store_true", help="强制重新处理")
    parser.add_argument("--create-review", action="store_true", help="创建人工校验文件")
    
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
    normalized_dir = Path(args.normalized_dir)
    output_dir = Path(args.output_dir)
    
    if not normalized_dir.exists():
        logger.error(f"标准化目录不存在: {normalized_dir}")
        return
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("开始章节切分")
    
    # 处理文档
    results = process_document(normalized_dir, output_dir, config, args.document_id, args.force)
    
    # 创建人工校验文件
    if args.create_review:
        review_file = create_review_file(output_dir)
        logger.info(f"人工校验文件已创建: {review_file}")
    
    # 输出统计
    logger.info("章节切分完成!")
    logger.info(f"成功: {results['success']}")
    logger.info(f"跳过: {results['skipped']}")
    logger.info(f"错误: {results['error']}")
    logger.info(f"总章节数: {results['total_sections']}")


if __name__ == "__main__":
    main()
