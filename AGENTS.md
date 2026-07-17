# 系统架构设计师学习网站

## 项目概述

基于个人学习资料，建设本地优先的学习网站，支持章节浏览、知识点学习、练习题训练、错题本和学习进度追踪。

## 技术栈

- **前端**: Next.js App Router + TypeScript + Tailwind CSS + shadcn/ui
- **数据库**: SQLite + Drizzle ORM
- **资料处理**: Python 3.11 + MinerU API (PDF) + python-docx + python-pptx
- **全文检索**: SQLite FTS5

## 项目结构

```
system-architect-learning/
├── pipeline/          # 资料处理脚本 (Python)
├── data/              # 处理数据输出
├── materials/         # 原始资料软链接
├── web/               # Next.js 网站 (待创建)
├── tests/             # 测试
└── docs/              # 文档
```

## 关键命令

```bash
# 激活 Python 环境
source pipeline/.venv/bin/activate

# 扫描资料
python pipeline/scripts/scan_materials.py \
  --input materials/links/source \
  --output data/manifest/materials_manifest.jsonl \
  --summary data/manifest/materials_summary.json \
  --category-config pipeline/config/material_categories.yml

# 解析资料
python pipeline/scripts/parse_materials.py \
  --manifest data/manifest/processing_queue.jsonl \
  --output-dir data/extracted \
  --log-file data/logs/parse_materials.log

# 运行测试
python tests/test_parsing.py
```

## 当前进度

- [x] 阶段 0: 项目初始化
- [x] 阶段 1: 资料清点和分类 (226 个文件, 2.47GB)
- [x] 阶段 2: 资料解析 (MinerU API)
- [x] 阶段 3: Markdown 标准化
- [x] 阶段 4: 建立课程结构 (391 个章节)
- [x] 阶段 5: 建立知识点模型 (38 个知识点)
- [x] 阶段 6: 题库结构化 (6 道题, 待人工补充)
- [x] 阶段 7: 创建 Web 项目 (Next.js + SQLite)
- [x] 阶段 8: 数据导入网站数据库 (3科目, 19章节, 38知识点, 6题目)
- [x] 阶段 9: 实现网站页面 (首页, 学习, 题库, 错题本)
- [ ] 阶段 10: 学习进度和统计
- [ ] 阶段 11: 全文搜索
- [ ] 阶段 12-16: 测试和部署

## 试点教材

- 文件: `系统架构设计师教程划重点版本(1).pdf`
- 页数: 657 页
- 字符数: 544,936
- 解析状态: 成功

## 重要说明

1. 原始资料通过软链接访问，不直接修改
2. 所有数据处理脚本支持重复运行
3. PDF 解析使用 MinerU API，需要设置 `MINERU_API_TOKEN` 环境变量
4. 执行方案详情见 `docs/execution-plan.md` (已加入 .gitignore)

## Git 提交规范

```
chore: 初始化和配置
feat: 新功能
fix: 修复
docs: 文档
test: 测试
refactor: 重构
```
