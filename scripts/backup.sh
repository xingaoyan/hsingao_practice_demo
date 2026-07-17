#!/bin/bash

# 数据库备份脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
BACKUP_FILE="$BACKUP_DIR/learning-$TIMESTAMP.db"

echo "系统架构设计师学习网站 - 数据库备份"
echo "项目根目录: $PROJECT_ROOT"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 检查数据库文件是否存在
DB_FILE="$PROJECT_ROOT/data/database/learning.db"
if [ ! -f "$DB_FILE" ]; then
    echo "警告: 数据库文件不存在: $DB_FILE"
    echo "跳过数据库备份"
else
    echo "备份数据库..."
    cp "$DB_FILE" "$BACKUP_FILE"
    echo "数据库已备份到: $BACKUP_FILE"
fi

# 备份人工校验后的知识点和题库
echo "备份结构化数据..."
STRUCTURED_DIR="$PROJECT_ROOT/data/structured"
if [ -d "$STRUCTURED_DIR" ]; then
    tar -czf "$BACKUP_DIR/structured-$TIMESTAMP.tar.gz" -C "$PROJECT_ROOT" data/structured
    echo "结构化数据已备份到: $BACKUP_DIR/structured-$TIMESTAMP.tar.gz"
fi

# 备份个人笔记和学习记录（如果数据库存在）
if [ -f "$DB_FILE" ]; then
    echo "备份完成!"
    echo ""
    echo "备份文件:"
    ls -lh "$BACKUP_DIR"/*"$TIMESTAMP"*
else
    echo "备份完成（无数据库备份）"
fi

echo ""
echo "恢复方法:"
echo "1. 数据库恢复: cp $BACKUP_FILE $DB_FILE"
echo "2. 结构化数据恢复: tar -xzf $BACKUP_DIR/structured-$TIMESTAMP.tar.gz -C $PROJECT_ROOT"