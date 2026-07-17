#!/usr/bin/env python3
"""
统一解析入口
"""

import os
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from tqdm import tqdm

# 添加父目录到 Python 路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers import PDFParser, DOCXParser, PPTXParser, TextParser, ExcelParser


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


def get_parser(file_type: str):
    """根据文件类型获取解析器"""
    parsers = {
        'pdf': PDFParser,
        'docx': DOCXParser,
        'doc': DOCXParser,
        'pptx': PPTXParser,
        'ppt': PPTXParser,
        'xlsx': ExcelParser,
        'xls': ExcelParser,
        'markdown': TextParser,
        'text': TextParser,
    }
    
    parser_class = parsers.get(file_type)
    if parser_class:
        return parser_class()
    return None


def parse_single_file(file_info: Dict, output_dir: Path, force: bool = False) -> Dict:
    """解析单个文件"""
    logger = logging.getLogger(__name__)
    
    document_id = file_info['file_id']
    file_type = file_info['file_type']
    file_path = Path(file_info['absolute_path'])
    
    # 检查输出目录
    doc_output_dir = output_dir / document_id
    output_file = doc_output_dir / 'parsed.json'
    
    # 如果已存在且不强制，跳过
    if output_file.exists() and not force:
        logger.info(f"跳过已解析文件: {file_info['filename']}")
        return {
            'document_id': document_id,
            'status': 'skipped',
            'message': '已存在解析结果'
        }
    
    # 获取解析器
    parser = get_parser(file_type)
    if not parser:
        logger.warning(f"不支持的文件类型: {file_type}")
        return {
            'document_id': document_id,
            'status': 'unsupported',
            'message': f'不支持的文件类型: {file_type}'
        }
    
    # 检查文件是否存在
    if not file_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return {
            'document_id': document_id,
            'status': 'error',
            'message': f'文件不存在: {file_path}'
        }
    
    try:
        # 解析文件
        logger.info(f"开始解析: {file_info['filename']}")
        result = parser.parse(file_path, document_id)
        
        # 创建输出目录
        doc_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存解析结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        
        # 生成解析报告
        report = {
            'document_id': document_id,
            'page_count': len(result.pages),
            'text_page_count': sum(1 for page in result.pages if page.text.strip()),
            'scan_page_count': sum(1 for page in result.pages if not page.text.strip()),
            'empty_page_count': sum(1 for page in result.pages if not page.text),
            'character_count': sum(len(page.text) for page in result.pages),
            'parse_status': 'success',
            'warnings': result.warnings
        }
        
        report_file = doc_output_dir / 'parse_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"解析完成: {file_info['filename']}, 页数: {len(result.pages)}")
        
        return {
            'document_id': document_id,
            'status': 'success',
            'page_count': len(result.pages),
            'character_count': report['character_count'],
            'warnings': len(result.warnings)
        }
        
    except Exception as e:
        logger.error(f"解析文件 {file_info['filename']} 时出错: {e}")
        return {
            'document_id': document_id,
            'status': 'error',
            'message': str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="统一解析入口")
    parser.add_argument("--manifest", required=True, help="处理队列文件路径")
    parser.add_argument("--output-dir", required=True, help="输出目录路径")
    parser.add_argument("--log-file", help="日志文件路径")
    parser.add_argument("--only-file-id", help="只处理指定文件ID")
    parser.add_argument("--only-type", help="只处理指定文件类型")
    parser.add_argument("--force", action="store_true", help="强制重新解析")
    parser.add_argument("--skip-existing", action="store_true", help="跳过已存在的文件")
    parser.add_argument("--max-files", type=int, help="最大处理文件数")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_file)
    logger = logging.getLogger(__name__)
    
    # 加载处理队列
    manifest_file = Path(args.manifest)
    if not manifest_file.exists():
        logger.error(f"处理队列文件不存在: {manifest_file}")
        return
    
    # 读取文件信息
    file_infos = []
    with open(manifest_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                file_infos.append(json.loads(line))
    
    logger.info(f"加载了 {len(file_infos)} 个文件信息")
    
    # 过滤文件
    if args.only_file_id:
        file_infos = [f for f in file_infos if f['file_id'] == args.only_file_id]
    
    if args.only_type:
        file_infos = [f for f in file_infos if f['file_type'] == args.only_type]
    
    if args.max_files:
        file_infos = file_infos[:args.max_files]
    
    logger.info(f"过滤后剩余 {len(file_infos)} 个文件")
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理文件
    results = {
        'success': 0,
        'skipped': 0,
        'error': 0,
        'unsupported': 0
    }
    
    for file_info in tqdm(file_infos, desc="解析文件"):
        result = parse_single_file(file_info, output_dir, args.force)
        
        status = result.get('status', 'unknown')
        if status in results:
            results[status] += 1
        
        # 记录警告
        if result.get('warnings', 0) > 0:
            logger.warning(f"文件 {file_info['filename']} 有 {result['warnings']} 个警告")
    
    # 输出统计
    logger.info("解析完成!")
    logger.info(f"成功: {results['success']}")
    logger.info(f"跳过: {results['skipped']}")
    logger.info(f"错误: {results['error']}")
    logger.info(f"不支持: {results['unsupported']}")


if __name__ == "__main__":
    main()