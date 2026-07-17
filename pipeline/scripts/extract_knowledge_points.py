#!/usr/bin/env python3
"""
知识点提取脚本
从结构化章节中提取知识点
"""

import json
import re
import hashlib
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


def generate_knowledge_point_id(section_id: str, title: str, index: int) -> str:
    """生成稳定的知识点ID"""
    content = f"{section_id}:{title}:{index}"
    hash_value = hashlib.md5(content.encode()).hexdigest()[:12]
    return f"kp_{hash_value}"


def split_section_into_knowledge_points(section: Dict) -> List[Dict]:
    """
    将章节拆分为知识点
    根据内容长度和结构进行拆分
    """
    content = section.get('content_markdown', '')
    section_id = section.get('section_id', '')
    title = section.get('title', '')
    
    if not content or len(content.strip()) < 50:
        return []
    
    knowledge_points = []
    
    # 检查是否有子标题
    lines = content.split('\n')
    current_kp_content = []
    current_kp_title = title
    kp_index = 0
    
    for line in lines:
        # 检测子标题（使用数字编号模式）
        sub_heading_match = re.match(r'^(\d+[\.\)]\s*|[\(（]\d+[\)）]\s*|[一二三四五六七八九十]+[\、\.]\s*)(.+)$', line.strip())
        
        if sub_heading_match and len(line.strip()) < 100:
            # 保存之前的知识点
            if current_kp_content:
                kp_content = '\n'.join(current_kp_content).strip()
                if len(kp_content) >= 50:  # 至少50个字符才作为知识点
                    knowledge_points.append({
                        'title': current_kp_title,
                        'content': kp_content,
                        'index': kp_index
                    })
                    kp_index += 1
            
            # 开始新知识点
            current_kp_title = sub_heading_match.group(2).strip()
            current_kp_content = []
        else:
            current_kp_content.append(line)
    
    # 保存最后一个知识点
    if current_kp_content:
        kp_content = '\n'.join(current_kp_content).strip()
        if len(kp_content) >= 50:
            knowledge_points.append({
                'title': current_kp_title,
                'content': kp_content,
                'index': kp_index
            })
    
    # 如果没有子标题，将整个内容作为一个知识点
    if not knowledge_points and len(content.strip()) >= 100:
        # 如果内容太长，尝试按段落拆分
        if len(content) > 2000:
            paragraphs = content.split('\n\n')
            current_content = []
            current_length = 0
            
            for i, para in enumerate(paragraphs):
                if current_length + len(para) > 1500 and current_content:
                    knowledge_points.append({
                        'title': f"{title} - 第{len(knowledge_points)+1}部分",
                        'content': '\n\n'.join(current_content).strip(),
                        'index': len(knowledge_points)
                    })
                    current_content = [para]
                    current_length = len(para)
                else:
                    current_content.append(para)
                    current_length += len(para)
            
            if current_content:
                knowledge_points.append({
                    'title': f"{title} - 第{len(knowledge_points)+1}部分",
                    'content': '\n\n'.join(current_content).strip(),
                    'index': len(knowledge_points)
                })
        else:
            knowledge_points.append({
                'title': title,
                'content': content.strip(),
                'index': 0
            })
    
    return knowledge_points


def extract_tags(title: str, content: str) -> List[str]:
    """从内容中提取标签"""
    tags = set()
    
    # 常见技术关键词
    tech_keywords = [
        '架构', '设计模式', 'MVC', 'MVP', 'SOA', '微服务', '分层', '管道',
        '过滤器', '客户端', '服务器', '总线', '仓库', '解释器', '进程',
        '线程', '并发', '同步', '异步', '消息', '队列', '缓存', '负载',
        '均衡', '容错', '冗余', '备份', '恢复', '安全', '认证', '授权',
        '加密', '解密', '接口', '抽象', '封装', '继承', '多态',
        'ATAM', 'SAAM', '质量属性', '性能', '可用性', '可修改性',
        '安全性', '可测试性', '易用性'
    ]
    
    text = title + ' ' + content[:500]
    
    for keyword in tech_keywords:
        if keyword in text:
            tags.add(keyword)
    
    return list(tags)[:10]  # 最多10个标签


def extract_exam_points(title: str, content: str) -> List[str]:
    """提取考试关注点"""
    exam_points = []
    
    # 查找"重点"、"关键"、"注意"等提示词
    patterns = [
        r'(?:重点|关键|核心|重要)[：:](.+?)(?:\n|$)',
        r'(?:注意|考点|考试)[：:](.+?)(?:\n|$)',
        r'(?:特点|特征|优势|缺点)[：:](.+?)(?:\n|$)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content[:1000])
        for match in matches:
            point = match.strip()
            if point and len(point) < 100:
                exam_points.append(point)
    
    # 如果没有找到明确的考点，根据标题生成
    if not exam_points:
        if '概述' in title or '定义' in title:
            exam_points.append(f"理解{title}的概念")
        elif '特点' in title or '特征' in title:
            exam_points.append(f"掌握{title}")
        elif '分类' in title or '类型' in title:
            exam_points.append(f"区分{title}")
        elif '方法' in title or '技术' in title:
            exam_points.append(f"应用{title}")
    
    return exam_points[:5]  # 最多5个考点


def estimate_difficulty(title: str, content: str) -> int:
    """估计难度等级 (1-5)"""
    difficulty = 3  # 默认中等
    
    # 根据内容特征调整难度
    if '概述' in title or '定义' in title or '概念' in title:
        difficulty = 1  # 基础概念
    elif '分类' in title or '类型' in title:
        difficulty = 2  # 分类知识
    elif '设计' in title or '实现' in title:
        difficulty = 4  # 设计实现
    elif '评估' in title or '分析' in title:
        difficulty = 4  # 评估分析
    elif '综合' in title or '案例' in title:
        difficulty = 5  # 综合应用
    
    # 根据内容长度调整
    if len(content) > 2000:
        difficulty = min(difficulty + 1, 5)
    
    return difficulty


def estimate_importance(title: str, chapter: str) -> int:
    """估计重要程度 (1-5)"""
    importance = 3  # 默认中等
    
    # 高频考点
    high_importance_keywords = [
        '架构风格', '设计模式', '质量属性', 'ATAM', 'SOA', '微服务',
        'MVC', '分层', '评估', '中间件'
    ]
    
    for keyword in high_importance_keywords:
        if keyword in title:
            importance = 5
            break
    
    # 中频考点
    medium_importance_keywords = [
        '概述', '分类', '特点', '关键技术', '组成'
    ]
    
    for keyword in medium_importance_keywords:
        if keyword in title:
            importance = max(importance, 3)
    
    return importance


def process_sections(structured_dir: Path, output_dir: Path, chapter_id: str = None, force: bool = False) -> Dict:
    """处理章节，提取知识点"""
    logger = logging.getLogger(__name__)
    
    results = {
        'success': 0,
        'skipped': 0,
        'error': 0,
        'total_knowledge_points': 0
    }
    
    # 加载章节数据
    all_sections = []
    for doc_dir in structured_dir.iterdir():
        if doc_dir.is_dir():
            sections_file = doc_dir / 'sections.jsonl'
            if sections_file.exists():
                with open(sections_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            section = json.loads(line)
                            all_sections.append(section)
    
    # 过滤指定章节
    if chapter_id:
        sections_to_process = [s for s in all_sections if s.get('predicted_chapter') == chapter_id]
    else:
        sections_to_process = all_sections
    
    logger.info(f"找到 {len(sections_to_process)} 个待处理章节")
    
    # 提取知识点
    all_knowledge_points = []
    
    for section in tqdm(sections_to_process, desc="提取知识点"):
        try:
            kps = split_section_into_knowledge_points(section)
            
            for kp in kps:
                kp_id = generate_knowledge_point_id(
                    section.get('section_id', ''),
                    kp['title'],
                    kp['index']
                )
                
                knowledge_point = {
                    'knowledge_point_id': kp_id,
                    'title': kp['title'],
                    'subject_id': 'comprehensive',  # 默认综合知识
                    'chapter_id': section.get('predicted_chapter', ''),
                    'section_id': section.get('section_id', ''),
                    'summary': kp['content'][:200] + '...' if len(kp['content']) > 200 else kp['content'],
                    'content_markdown': kp['content'],
                    'importance': estimate_importance(kp['title'], section.get('predicted_chapter', '')),
                    'difficulty': estimate_difficulty(kp['title'], kp['content']),
                    'tags': extract_tags(kp['title'], kp['content']),
                    'exam_points': extract_exam_points(kp['title'], kp['content']),
                    'source_references': [
                        {
                            'document_id': section.get('document_id', ''),
                            'page_start': section.get('source_page_start', 0),
                            'page_end': section.get('source_page_end', 0)
                        }
                    ],
                    'review_status': 'pending'
                }
                
                all_knowledge_points.append(knowledge_point)
            
        except Exception as e:
            logger.error(f"处理章节 {section.get('title', '')} 时出错: {e}")
            results['error'] += 1
    
    # 保存知识点
    output_file = output_dir / 'knowledge_points.jsonl'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for kp in all_knowledge_points:
            f.write(json.dumps(kp, ensure_ascii=False) + '\n')
    
    results['success'] = len(sections_to_process)
    results['total_knowledge_points'] = len(all_knowledge_points)
    
    return results


def create_knowledge_point_review(output_dir: Path) -> Path:
    """创建知识点人工校验文件"""
    review_file = output_dir / 'knowledge_point_review.csv'
    
    kps_file = output_dir / 'knowledge_points.jsonl'
    if not kps_file.exists():
        return None
    
    with open(review_file, 'w', encoding='utf-8') as f:
        f.write('knowledge_point_id,title,chapter_id,importance,difficulty,tags_count,exam_points_count,review_status,review_comment\n')
        
        with open(kps_file, 'r', encoding='utf-8') as kf:
            for line in kf:
                if line.strip():
                    kp = json.loads(line)
                    f.write(f"{kp.get('knowledge_point_id', '')},")
                    f.write(f"\"{kp.get('title', '')}\",")
                    f.write(f"{kp.get('chapter_id', '')},")
                    f.write(f"{kp.get('importance', 0)},")
                    f.write(f"{kp.get('difficulty', 0)},")
                    f.write(f"{len(kp.get('tags', []))},")
                    f.write(f"{len(kp.get('exam_points', []))},")
                    f.write(f"{kp.get('review_status', 'pending')},")
                    f.write(f"\n")
    
    return review_file


def main():
    parser = argparse.ArgumentParser(description="知识点提取脚本")
    parser.add_argument("--structured-dir", required=True, help="结构化数据目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--chapter-id", help="只处理指定章节ID (如 architecture-design)")
    parser.add_argument("--log-file", help="日志文件路径")
    parser.add_argument("--force", action="store_true", help="强制重新处理")
    parser.add_argument("--create-review", action="store_true", help="创建人工校验文件")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_file)
    logger = logging.getLogger(__name__)
    
    # 检查目录
    structured_dir = Path(args.structured_dir)
    output_dir = Path(args.output_dir)
    
    if not structured_dir.exists():
        logger.error(f"结构化数据目录不存在: {structured_dir}")
        return
    
    logger.info("开始知识点提取")
    
    # 处理章节
    results = process_sections(structured_dir, output_dir, args.chapter_id, args.force)
    
    # 创建人工校验文件
    if args.create_review:
        review_file = create_knowledge_point_review(output_dir)
        if review_file:
            logger.info(f"知识点校验文件已创建: {review_file}")
    
    # 输出统计
    logger.info("知识点提取完成!")
    logger.info(f"处理章节数: {results['success']}")
    logger.info(f"提取知识点数: {results['total_knowledge_points']}")
    logger.info(f"错误: {results['error']}")


if __name__ == "__main__":
    main()
