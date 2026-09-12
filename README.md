# 📚 Learning Logs - 现代化全栈树形知识库系统

> 基于 **Django + PostgreSQL + Cloudflare R2** 构建的树形结构知识管理与动态博客系统。针对长文本创作、复杂树状归档及中文模糊搜索场景进行了深度性能与架构优化。

[![Django](https://img.shields.io/badge/Django-6.1-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20(Mandatory)-blue.svg)]()
[![Cloudflare R2](https://img.shields.io/badge/Storage-Cloudflare%20R2-orange.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[🌐 在线演示 (Live Demo)](https://www.tqw740.top)

---

## 核心技术亮点 (Engineering Highlights)

- **高性能中文加权拼音搜索**：基于 PostgreSQL 原生 `pg_trgm` (Trigram Similarity) 与 **GIN索引**，支持拼音和错字容忍，并且使用了加权算法：`标题(×2.5) > 主题(×1.8) > 作者(×1.5) > 正文(×1.0)`。
- **云原生对象存储**：使用了 Cloudflare R2，前端请求后端预签名 URL 后直传图片至云端，**零服务器与带宽占用**，按 `posts/YYYY/MM/UUID.ext` 自动归档。
- **MPTT 无限级树形知识归档**：使用 `django-mptt` 实现多层级目录树（预排序遍历树算法），结合 `pypinyin` 自动将中文主题转化为语义化 Slug URL (如 `/user/biancheng/django/`)。
- **严格的安全与防御策略**：
  - **XSS 防护**：Markdown 经 `python-markdown` 解析后，强制通过 `bleach` 白名单过滤清洗入库/出库。
  - **水平越权防御**：采用 `@login_required` + 强制 `request.user == topic.owner` 校验，未授权访问统一返回 `404`（避免泄露资源存在性）。
- **查询与前端性能调优**：最新帖子流采用 `defer('text')` 避免拉取大文本字段；前端基于 `localStorage` 状态在 DOM 挂载前防闪烁渲染；静态资源经 WhiteNoise 压缩交付。

---

## 系统功能 (Features)

### 1. 知识树与分类管理

- 基于 `MPTTModel` 的无限层级分类树，支持快速获取祖先路径生成面包屑导航。
- 主题 Slug 实时 AJAX 校验与预览，严格白名单正则过滤非法字符。

### 2. 笔记撰写与 Markddown 沉浸体验

- 集成 **Vditor** 所见即所得 (WYSIWYG) 编辑器。
- 支持截图 `Ctrl + V` 粘贴直传、工具栏上传。
- 提交前表单 JS 自动双向绑定 Markdown 源码。

### 3. 用户与权限控制

- 访客视图：公开浏览主页、笔记详情、最新流及全文搜索。
- 作者视图：独立账号空间，仅创建者拥有对应主题树及笔记的增删改查权限。

---

## 技术栈 (Tech Stack)

| 领域 | 核心技术选型 | 说明 |
| :--- | :--- | :--- |
| **后端框架** | Django + Gunicorn | 核心业务逻辑与 API 支持 |
| **核心数据库** | **PostgreSQL (强制)** | 依赖 `pg_trgm` 扩展与 GIN 倒排索引 |
| **对象存储** | Cloudflare R2 | S3 协议兼容，负责附件与插图存储（预签名直传） |
| **前端展现** | Bootstrap 5 + Vditor | 响应式布局 + 现代化 Markdown 编辑器 |
| **分词/算法** | `pypinyin` + `django-mptt` | 中文 Slug 拼音转化与树形算法 |
| **安全过滤** | `bleach` | HTML 白名单清洗，抵御 XSS 注入 |
| **部署托管** | Vercel Serverless + WhiteNoise | 生产环境无缝部署与静态资源压缩托管 |

---

## 项目结构说明 (Architecture)

```text
├── ll_project/               # Django 项目全局配置 (settings / urls / wsgi)
├── accounts/                 # 用户鉴权模块 (注册、登录、登出)
├── learning_logs/            # 核心业务应用
│   ├── models/               # Topic (树形模型) 与 Entry (笔记正文) 模型
│   ├── views/                # 业务视图（按功能拆解为 5 个独立模块）
│   │   ├── search_views.py   # PostgreSQL TrigramSimilarity 加权搜索模块
│   │   ├── R2_views.py       # R2 预签名 URL 签发模块
│   │   └── ...
│   ├── templatetags/         # 自定义 Markdown 解析与 Bleach 过滤标签
│   └── static/vditor/        # Vditor 编辑器本地化静态资源
├── manage.py
└── requirements.txt
```

---

## 本地运行指南 (Getting Started)

### 1. 前置依赖

- Python >= 3.10
- **PostgreSQL >= 13** *(由于依赖 pg_trgm 扩展，不可使用 SQLite)*

### 2. 克隆项目与安装依赖

```bash
git clone https://github.com/tqw740/my_blog.git
cd my_blog

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. 配置环境变量

在根目录新建 `.env` 文件，填入以下变量：

```env
# Django 配置
SECRET_KEY=your-django-secret-key
DEBUG=True

# PostgreSQL 数据库配置 (强制)
DATABASE_URL=postgres://user:password@localhost:5432/learning_logs

# Cloudflare R2 存储配置
R2_ACCOUNT_ID=your_cloudflare_account_id
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
R2_PUBLIC_DOMAIN=https://your-custom-r2-domain.com
```

### 4. 初始化数据库与索引

```bash
# 执行数据库迁移（含 GIN trgm 索引迁移）
python manage.py migrate

# 创建超级管理员
python manage.py createsuperuser
```

> **注意**：数据库迁移 `0004_enable_trigram` 会自动创建 `pg_trgm` 扩展。请确保 PostgreSQL 用户拥有创建 Extension 的权限。

### 5. 启动本地开发服务

```bash
python manage.py runserver
```

访问浏览器 [http://127.0.0.1:8000](http://127.0.0.1:8000) 即可开始使用。

---

## 部署说明 (Deployment)

本项目专为 **Vercel** 部署优化：

1. 静态资源由 `whitenoise` 接管压缩与缓存；
2. 数据库推荐托管在 Neon / Supabase (PostgreSQL 实例)；
3. 对象存储直传 R2 绕过了 Vercel 的 Serverless Payload 大小及超时限制。

---

## 开源协议 (License)

本项目采用 [MIT License](LICENSE) 开源。
