# 系统架构设计师学习网站

基于个人学习资料，建设本地优先的学习网站，支持章节浏览、知识点学习、练习题训练、错题本和学习进度追踪。

## 技术架构

- **前端**: Next.js App Router + TypeScript + Tailwind CSS + shadcn/ui
- **数据库**: SQLite + Drizzle ORM
- **资料处理**: Python 3.11 + PyMuPDF + python-docx + python-pptx
- **全文检索**: SQLite FTS5

## 资料目录配置

资料目录通过环境变量 `MATERIALS_ROOT` 配置。当前软链接位置：

```
materials/links/source -> 原始资料目录
```

## Python 环境初始化

```bash
cd pipeline
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 数据处理命令

### 扫描资料

```bash
cd $PROJECT_ROOT
source pipeline/.venv/bin/activate

python pipeline/scripts/scan_materials.py \
  --input materials/links/source \
  --output data/manifest/materials_manifest.jsonl \
  --summary data/manifest/materials_summary.json \
  --category-config pipeline/config/material_categories.yml
```

## Web 启动方式

```bash
cd web
npm run dev
```

## 项目目录

```
system-architect-learning/
├── pipeline/          # 资料处理脚本
├── data/              # 处理数据输出
├── materials/         # 原始资料软链接
├── web/               # Next.js 网站
├── tests/             # 测试
└── docs/              # 文档
```

## 当前进度

- [x] 阶段 0: 项目初始化
- [x] 阶段 1: 资料清点和分类
- [x] 阶段 2: 资料解析（试点教材完成）
- [ ] 阶段 3: Markdown 标准化
- [ ] 阶段 4: 建立课程结构
- [ ] 阶段 5: 建立知识点模型
- [ ] 阶段 6: 题库结构化
- [ ] 阶段 7: 创建 Web 项目
- [ ] 阶段 8: 数据导入网站数据库
- [ ] 阶段 9: 实现网站页面

## 试点教材

已选择以下教材作为试点：

- 文件：`★★★26年系统架构师全套资料/02. 教材最新+知识点/03 系统架构设计师教程划重点版本(1).pdf`
- 页数：657 页
- 字符数：544,936
- 解析状态：成功
- 警告：第 577 页可能是扫描页（文本内容较少）
