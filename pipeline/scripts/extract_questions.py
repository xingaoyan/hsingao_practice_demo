#!/usr/bin/env python3
"""
题目提取脚本
从结构化章节中提取题目
"""

import json
import re
import hashlib
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
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


def generate_question_id(source_type: str, year: int, subject_id: str, number: int) -> str:
    """生成稳定的题目ID"""
    if source_type == 'past_exam':
        return f"q-{year}-{subject_id}-{number:03d}"
    else:
        content = f"{source_type}:{subject_id}:{number}"
        hash_value = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"q-{hash_value}"


def detect_question_type(text: str) -> str:
    """检测题型"""
    text_lower = text.lower()
    
    if '单选' in text_lower or '选择一个' in text_lower:
        return 'single_choice'
    elif '多选' in text_lower or '选择多个' in text_lower:
        return 'multiple_choice'
    elif '判断' in text_lower or '对错' in text_lower or '是否' in text_lower:
        return 'true_false'
    elif '简答' in text_lower or '简述' in text_lower or '说明' in text_lower:
        return 'short_answer'
    else:
        return 'single_choice'  # 默认单选


def parse_choice_options(text: str) -> List[Dict]:
    """解析选择题选项"""
    options = []
    
    # 匹配 A. B. C. D. 格式
    pattern = r'([A-Z])[\.、]\s*(.+?)(?=[A-Z][\.、]|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for key, value in matches:
        options.append({
            'key': key,
            'text': value.strip()
        })
    
    return options


def extract_questions_from_content(content: str, source_info: Dict) -> List[Dict]:
    """从内容中提取题目"""
    questions = []
    
    # 查找题目模式
    # 模式1: 数字. 题目内容
    # 模式2: 【题目X】
    # 模式3: 第X题
    
    lines = content.split('\n')
    current_question = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 检测题目开始
        question_match = re.match(r'^(?:第?\s*(\d+)\s*[\.、题]|【题[目]?(\d+)】)\s*(.+)$', line)
        
        if question_match:
            # 保存之前的题目
            if current_question:
                current_question['question_text'] = '\n'.join(current_content).strip()
                if current_question['question_text']:
                    questions.append(current_question)
            
            # 开始新题目
            number = question_match.group(1) or question_match.group(2)
            question_text = question_match.group(3)
            
            current_question = {
                'question_number': int(number) if number else len(questions) + 1,
                'source_info': source_info
            }
            current_content = [question_text] if question_text else []
        else:
            current_content.append(line)
    
    # 保存最后一个题目
    if current_question:
        current_question['question_text'] = '\n'.join(current_content).strip()
        if current_question['question_text']:
            questions.append(current_question)
    
    return questions


def process_sections_for_questions(structured_dir: Path, output_dir: Path, source_type: str = 'material_exercise') -> Dict:
    """从章节中提取题目"""
    logger = logging.getLogger(__name__)
    
    results = {
        'success': 0,
        'error': 0,
        'total_questions': 0
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
    
    # 查找可能包含题目的章节
    question_sections = []
    for section in all_sections:
        title = section.get('title', '').lower()
        content = section.get('content_markdown', '').lower()
        
        # 检查是否为题目相关章节
        if any(keyword in title for keyword in ['练习', '习题', '真题', '试题', '测试', '答案']):
            question_sections.append(section)
        elif any(keyword in content[:500] for keyword in ['单选', '多选', '判断', '答案', '解析']):
            question_sections.append(section)
    
    logger.info(f"找到 {len(question_sections)} 个可能包含题目的章节")
    
    # 提取题目
    all_questions = []
    
    for section in tqdm(question_sections, desc="提取题目"):
        try:
            source_info = {
                'document_id': section.get('document_id', ''),
                'section_id': section.get('section_id', ''),
                'page_start': section.get('source_page_start', 0),
                'page_end': section.get('source_page_end', 0)
            }
            
            questions = extract_questions_from_content(
                section.get('content_markdown', ''),
                source_info
            )
            
            for q in questions:
                question_text = q.get('question_text', '')
                
                # 检测题型
                question_type = detect_question_type(question_text)
                
                # 解析选项
                options = parse_choice_options(question_text)
                
                # 生成题目ID
                question_id = generate_question_id(
                    source_type,
                    0,  # 年份待补充
                    section.get('predicted_chapter', 'general'),
                    q.get('question_number', 0)
                )
                
                question = {
                    'question_id': question_id,
                    'question_type': question_type,
                    'source_type': source_type,
                    'year': None,
                    'subject_id': 'comprehensive',
                    'question_text': question_text,
                    'options': options,
                    'correct_answer': [],  # 待人工补充
                    'analysis': '',  # 待人工补充
                    'difficulty': 3,
                    'knowledge_point_ids': [],  # 待关联
                    'source_reference': source_info,
                    'review_status': 'pending'
                }
                
                all_questions.append(question)
            
        except Exception as e:
            logger.error(f"处理章节 {section.get('title', '')} 时出错: {e}")
            results['error'] += 1
    
    # 保存题目
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'questions.jsonl'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for q in all_questions:
            f.write(json.dumps(q, ensure_ascii=False) + '\n')
    
    results['success'] = len(question_sections)
    results['total_questions'] = len(all_questions)
    
    return results


def create_question_review(output_dir: Path) -> Path:
    """创建题目人工校验文件"""
    review_file = output_dir / 'question_review.csv'
    
    questions_file = output_dir / 'questions.jsonl'
    if not questions_file.exists():
        return None
    
    with open(review_file, 'w', encoding='utf-8') as f:
        f.write('question_id,question_type,source_type,subject_id,has_options,has_answer,review_status,review_comment\n')
        
        with open(questions_file, 'r', encoding='utf-8') as qf:
            for line in qf:
                if line.strip():
                    q = json.loads(line)
                    f.write(f"{q.get('question_id', '')},")
                    f.write(f"{q.get('question_type', '')},")
                    f.write(f"{q.get('source_type', '')},")
                    f.write(f"{q.get('subject_id', '')},")
                    f.write(f"{'yes' if q.get('options') else 'no'},")
                    f.write(f"{'yes' if q.get('correct_answer') else 'no'},")
                    f.write(f"{q.get('review_status', 'pending')},")
                    f.write(f"\n")
    
    return review_file


def main():
    parser = argparse.ArgumentParser(description="题目提取脚本")
    parser.add_argument("--structured-dir", required=True, help="结构化数据目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--source-type", default="material_exercise", help="题目来源类型")
    parser.add_argument("--log-file", help="日志文件路径")
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
    
    logger.info("开始题目提取")
    
    # 处理章节
    results = process_sections_for_questions(structured_dir, output_dir, args.source_type)
    
    # 创建人工校验文件
    if args.create_review:
        review_file = create_question_review(output_dir)
        if review_file:
            logger.info(f"题目校验文件已创建: {review_file}")
    
    # 输出统计
    logger.info("题目提取完成!")
    logger.info(f"处理章节数: {results['success']}")
    logger.info(f"提取题目数: {results['total_questions']}")
    logger.info(f"错误: {results['error']}")


if __name__ == "__main__":
    main()
