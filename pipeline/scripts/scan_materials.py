#!/usr/bin/env python3
"""
扫描学习资料目录，生成文件清单和统计信息。
"""

import os
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
import yaml
from tqdm import tqdm


def calculate_sha256(file_path: Path) -> str:
    """计算文件的 SHA-256 哈希值"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def get_file_type(extension: str) -> str:
    """根据扩展名获取文件类型"""
    extension_map = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'doc',
        '.pptx': 'pptx',
        '.ppt': 'ppt',
        '.xlsx': 'xlsx',
        '.xls': 'xls',
        '.md': 'markdown',
        '.txt': 'text',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.bmp': 'image',
        '.mp4': 'video',
        '.avi': 'video',
        '.mov': 'video',
        '.wmv': 'video',
        '.mp3': 'audio',
        '.wav': 'audio',
        '.zip': 'archive',
        '.rar': 'archive',
        '.7z': 'archive',
        '.tar': 'archive',
        '.gz': 'archive',
    }
    return extension_map.get(extension.lower(), 'unknown')


def categorize_file(file_path: Path, categories_config: Dict) -> str:
    """根据文件路径和名称推断分类"""
    file_name = file_path.name.lower()
    path_str = str(file_path).lower()
    
    for category, config in categories_config.items():
        if category == '其他':
            continue
        keywords = config.get('keywords', [])
        for keyword in keywords:
            if keyword.lower() in file_name or keyword.lower() in path_str:
                return category
    
    return '其他'


def is_hidden_file(file_path: Path) -> bool:
    """检查是否为隐藏文件"""
    return any(part.startswith('.') for part in file_path.parts)


def should_skip_file(file_path: Path) -> bool:
    """检查是否应该跳过的文件"""
    skip_files = {'.ds_store', '.thumbs.db', 'desktop.ini'}
    return file_path.name.lower() in skip_files


def scan_directory(input_dir: Path, categories_config: Dict) -> List[Dict]:
    """扫描目录，返回文件信息列表"""
    files_info = []
    seen_hashes: Dict[str, str] = {}  # hash -> first_seen_path
    
    # 获取所有文件
    all_files = []
    for root, dirs, files in os.walk(input_dir):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            file_path = Path(root) / file
            if not is_hidden_file(file_path) and not should_skip_file(file_path):
                all_files.append(file_path)
    
    print(f"找到 {len(all_files)} 个文件")
    
    # 处理每个文件
    for file_path in tqdm(all_files, desc="扫描文件"):
        try:
            stat = file_path.stat()
            extension = file_path.suffix.lower()
            relative_path = file_path.relative_to(input_dir)
            
            # 计算哈希
            file_hash = calculate_sha256(file_path)
            
            # 检查重复
            is_duplicate = False
            if file_hash in seen_hashes:
                is_duplicate = True
                duplicate_of = seen_hashes[file_hash]
            else:
                seen_hashes[file_hash] = str(relative_path)
            
            # 获取文件信息
            file_info = {
                "file_id": file_hash,
                "relative_path": str(relative_path),
                "absolute_path": str(file_path),
                "filename": file_path.name,
                "extension": extension,
                "file_type": get_file_type(extension),
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "category": categorize_file(file_path, categories_config),
                "subject": None,
                "year": None,
                "parse_status": "pending",
                "is_duplicate": is_duplicate,
            }
            
            if is_duplicate:
                file_info["duplicate_of"] = duplicate_of
            
            files_info.append(file_info)
            
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            continue
    
    return files_info


def generate_summary(files_info: List[Dict]) -> Dict:
    """生成统计摘要"""
    summary = {
        "total_files": len(files_info),
        "by_type": {},
        "by_category": {},
        "by_extension": {},
        "total_size_bytes": 0,
        "duplicate_count": 0,
        "pending_count": 0,
    }
    
    for file_info in files_info:
        # 按类型统计
        file_type = file_info["file_type"]
        summary["by_type"][file_type] = summary["by_type"].get(file_type, 0) + 1
        
        # 按分类统计
        category = file_info["category"]
        summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        # 按扩展名统计
        extension = file_info["extension"]
        summary["by_extension"][extension] = summary["by_extension"].get(extension, 0) + 1
        
        # 总大小
        summary["total_size_bytes"] += file_info["size_bytes"]
        
        # 重复文件
        if file_info.get("is_duplicate", False):
            summary["duplicate_count"] += 1
        
        # 待处理数量
        if file_info["parse_status"] == "pending":
            summary["pending_count"] += 1
    
    # 转换总大小为可读格式
    total_size = summary["total_size_bytes"]
    if total_size < 1024:
        summary["total_size_readable"] = f"{total_size} B"
    elif total_size < 1024 * 1024:
        summary["total_size_readable"] = f"{total_size / 1024:.2f} KB"
    elif total_size < 1024 * 1024 * 1024:
        summary["total_size_readable"] = f"{total_size / (1024 * 1024):.2f} MB"
    else:
        summary["total_size_readable"] = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
    
    return summary


def main():
    parser = argparse.ArgumentParser(description="扫描学习资料目录")
    parser.add_argument("--input", required=True, help="输入目录路径")
    parser.add_argument("--output", required=True, help="输出 JSONL 文件路径")
    parser.add_argument("--summary", required=True, help="输出统计摘要 JSON 文件路径")
    parser.add_argument("--category-config", required=True, help="分类配置文件路径")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_file = Path(args.output)
    summary_file = Path(args.summary)
    category_config_file = Path(args.category_config)
    
    # 检查输入目录
    if not input_dir.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        return
    
    # 加载分类配置
    try:
        with open(category_config_file, 'r', encoding='utf-8') as f:
            categories_config = yaml.safe_load(f)['categories']
    except Exception as e:
        print(f"错误: 无法加载分类配置: {e}")
        return
    
    # 创建输出目录
    output_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"开始扫描目录: {input_dir}")
    
    # 扫描文件
    files_info = scan_directory(input_dir, categories_config)
    
    # 生成统计摘要
    summary = generate_summary(files_info)
    
    # 写入 JSONL 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for file_info in files_info:
            f.write(json.dumps(file_info, ensure_ascii=False) + '\n')
    
    # 写入统计摘要
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    # 输出统计信息
    print(f"\n扫描完成!")
    print(f"总文件数: {summary['total_files']}")
    print(f"总大小: {summary['total_size_readable']}")
    print(f"重复文件: {summary['duplicate_count']}")
    print(f"待处理文件: {summary['pending_count']}")
    
    print(f"\n按类型统计:")
    for file_type, count in sorted(summary['by_type'].items()):
        print(f"  {file_type}: {count}")
    
    print(f"\n按分类统计:")
    for category, count in sorted(summary['by_category'].items()):
        print(f"  {category}: {count}")
    
    print(f"\n按扩展名统计:")
    for extension, count in sorted(summary['by_extension'].items()):
        print(f"  {extension}: {count}")
    
    print(f"\n输出文件:")
    print(f"  文件清单: {output_file}")
    print(f"  统计摘要: {summary_file}")


if __name__ == "__main__":
    main()