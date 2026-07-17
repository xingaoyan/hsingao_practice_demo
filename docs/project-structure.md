# 项目结构图

```
system-architect-learning/
├── README.md                    # 项目说明
├── PROJECT_STATUS.md            # 项目状态报告
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git 忽略文件
│
├── pipeline/                    # 资料处理脚本
│   ├── requirements.txt         # Python 依赖
│   ├── .venv/                   # Python 虚拟环境
│   ├── config/
│   │   └── material_categories.yml  # 分类配置
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base.py              # 基础解析器
│   │   ├── pdf_parser.py        # PDF 解析器
│   │   ├── docx_parser.py       # DOCX 解析器
│   │   ├── pptx_parser.py       # PPTX 解析器
│   │   ├── text_parser.py       # 文本解析器
│   │   └── excel_parser.py      # Excel 解析器
│   ├── scripts/
│   │   ├── scan_materials.py    # 资料扫描脚本
│   │   ├── parse_materials.py   # 统一解析入口
│   │   └── validate_parsing.py  # 解析验证脚本
│   ├── processors/              # 数据处理（待实现）
│   └── validators/              # 数据验证（待实现）
│
├── data/                        # 处理数据输出
│   ├── manifest/
│   │   ├── materials_manifest.jsonl    # 文件清单
│   │   ├── materials_summary.json      # 统计摘要
│   │   └── processing_queue.jsonl      # 处理队列
│   ├── extracted/               # 解析结果
│   │   └── 8fde162be62c742f88df99a948b8b3a60d72533a61d4a9d6c602f0d25b285598/
│   │       ├── parsed.json      # 解析数据
│   │       └── parse_report.json # 解析报告
│   ├── normalized/              # 标准化 Markdown（待实现）
│   ├── structured/              # 结构化数据（待实现）
│   ├── questions/               # 题库数据（待实现）
│   ├── rejected/
│   │   └── unsupported_files.jsonl  # 不支持的文件
│   ├── logs/
│   │   ├── parse_materials.log  # 解析日志
│   │   └── validation_report.json # 验证报告
│   └── database/                # SQLite 数据库（待实现）
│
├── materials/                   # 原始资料
│   ├── raw/                     # 原始资料（可选）
│   └── links/
│       └── source -> /Users/hsingaoyen/Downloads/★★→高级系统架构设计师
│
├── web/                         # Next.js 网站（待实现）
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── db/
│   ├── public/
│   └── content/
│
├── scripts/                     # 项目脚本
│   ├── dev.sh                   # 开发服务器启动脚本
│   └── backup.sh                # 数据库备份脚本
│
├── tests/                       # 测试文件
│   ├── fixtures/
│   ├── pipeline/
│   └── web/
│
├── docs/                        # 文档
│   ├── progress-report.md       # 进度报告
│   ├── project-structure.md     # 项目结构图
│   ├── architecture.md          # 架构设计（待实现）
│   ├── data-model.md            # 数据模型（待实现）
│   ├── material-processing.md   # 资料处理文档（待实现）
│   └── acceptance-checklist.md  # 验收清单（待实现）
│
└── backups/                     # 备份文件
    └── structured-20260717-212330.tar.gz
```

## 关键文件说明

### 配置文件
- `pipeline/config/material_categories.yml`: 资料分类规则配置
- `.env.example`: 环境变量示例

### 核心脚本
- `pipeline/scripts/scan_materials.py`: 扫描资料目录，生成文件清单
- `pipeline/scripts/parse_materials.py`: 统一解析入口，支持多种文件格式
- `pipeline/scripts/validate_parsing.py`: 验证解析质量

### 解析器
- `pipeline/parsers/base.py`: 基础解析器类定义
- `pipeline/parsers/pdf_parser.py`: PDF 文件解析（基于 PyMuPDF）
- `pipeline/parsers/docx_parser.py`: DOCX 文件解析（基于 python-docx）
- `pipeline/parsers/pptx_parser.py`: PPTX 文件解析（基于 python-pptx）
- `pipeline/parsers/text_parser.py`: Markdown/TXT 文件解析
- `pipeline/parsers/excel_parser.py`: Excel 文件解析（基于 openpyxl）

### 数据文件
- `data/manifest/materials_manifest.jsonl`: 所有文件的清单
- `data/manifest/materials_summary.json`: 文件统计摘要
- `data/manifest/processing_queue.jsonl`: 待处理文件队列
- `data/rejected/unsupported_files.jsonl`: 不支持的文件列表

### 解析结果
- `data/extracted/<document_id>/parsed.json`: 解析后的文档数据
- `data/extracted/<document_id>/parse_report.json`: 解析质量报告

## 目录状态

| 目录 | 状态 | 说明 |
|------|------|------|
| `pipeline/` | ✅ 完成 | 资料处理脚本 |
| `data/manifest/` | ✅ 完成 | 资料清单和统计 |
| `data/extracted/` | 🔄 部分完成 | 试点教材已解析 |
| `data/normalized/` | ⏳ 待实现 | Markdown 标准化 |
| `data/structured/` | ⏳ 待实现 | 章节和知识点 |
| `data/questions/` | ⏳ 待实现 | 题库结构化 |
| `web/` | ⏳ 待实现 | Next.js 网站 |
| `tests/` | ⏳ 待实现 | 测试文件 |
| `docs/` | 🔄 部分完成 | 部分文档已创建 |

## 数据流

```
原始资料 (materials/)
    ↓
文件扫描 (scan_materials.py)
    ↓
文件清单 (data/manifest/)
    ↓
文件解析 (parse_materials.py)
    ↓
解析结果 (data/extracted/)
    ↓
Markdown 标准化 (待实现)
    ↓
标准化内容 (data/normalized/)
    ↓
章节切分 (待实现)
    ↓
结构化数据 (data/structured/)
    ↓
网站内容 (web/content/)
```

## 下一步工作

1. **阶段 3**: Markdown 标准化
   - 创建标准化规则
   - 实现页眉页脚检测
   - 实现标题层级恢复
   - 输出标准 Markdown

2. **阶段 4**: 建立课程结构
   - 定义科目和章节
   - 实现文档章节切分
   - 章节归类

3. **阶段 5**: 建立知识点模型
   - 知识点抽取
   - 知识点关系建立

4. **阶段 6**: 题库结构化
   - 题目抽取
   - 题目校验

5. **阶段 7**: 创建 Web 项目
   - 初始化 Next.js
   - 建立数据库 Schema

6. **阶段 8**: 数据导入网站数据库

7. **阶段 9**: 实现网站页面

---

**最后更新**: 2026-07-17