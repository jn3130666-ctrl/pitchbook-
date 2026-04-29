# VC/PE 每周市场观察

自动化流水线：抓取 PitchBook 邮件 → AI 摘要 → 生成周报 → 网页展示。

## 项目结构

```
├── fetch_emails.py        # 步骤1：IMAP 抓取 PitchBook 邮件
├── download_reports.py     # 步骤2：下载报告附件
├── analyze.py              # 步骤3：DeepSeek V4 Flash 中文摘要
├── generate_report.py      # 步骤4：生成 Markdown 周报
├── generate_index.py       # 生成 GitHub Pages 首页
├── main.py                 # 一键串联全部步骤
├── .env                    # 环境变量（不提交到 git）
├── .env.example            # 环境变量模板
├── requirements.txt        # Python 依赖
├── README.md               # 本文件
├── data/                   # 中间数据（不提交到 git）
│   ├── emails.json
│   └── analyzed.json
├── docs/                   # 生成的周报 Markdown（文档目录，可直接阅读）
│   └── YYYY-MM-DD-weekly.md
├── reports/                # 下载的报告文件
├── index.html              # GitHub Pages 首页
└── .github/workflows/
    └── weekly.yml          # GitHub Actions 定时任务
```

## 本地运行

```bash
# 1. 激活虚拟环境
source .venv/Scripts/activate

# 2. 配置 .env
cp .env.example .env
# 编辑 .env，填入邮箱和 API Key

# 3. 运行完整流水线
python main.py
```

## 环境变量

| 变量 | 说明 | 来源 |
|------|------|------|
| `EMAIL_HOST` | IMAP 服务器地址 | 邮箱服务商 |
| `EMAIL_USER` | 邮箱地址 | — |
| `EMAIL_PASS` | 邮箱授权码（非登录密码） | 邮箱设置 → POP3/SMTP/IMAP |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | https://platform.deepseek.com |

### 163 邮箱特别说明

- IMAP 服务器：`imap.163.com`，端口 `993`（SSL）
- 需要开启 IMAP 服务并生成**授权码**（不是邮箱登录密码）
- 脚本内置 `IMAP ID` 命令，规避 163 的 "Unsafe Login" 拦截

## GitHub Actions 定时任务

每周一北京时间 09:00 自动运行，同时更新 GitHub Pages。

### 1. 添加 Secrets

在仓库 **Settings → Secrets and variables → Actions → New repository secret** 添加：

| Secret | 说明 |
|--------|------|
| `EMAIL_HOST` | `imap.163.com` |
| `EMAIL_USER` | 你的 163 邮箱 |
| `EMAIL_PASS` | 163 授权码 |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |

### 2. 启用 GitHub Pages

仓库 **Settings → Pages** → Source 选择 **Deploy from branch** → **main** → **/ (root)** → Save

### 3. 手动触发

进入 Actions 页面 → 左侧 **VC/PE Weekly** → **Run workflow**

### 访问地址

```
https://<你的用户名>.github.io/<仓库名>/
```

## 依赖

```
pip install -r requirements.txt
```

主要依赖：
- `beautifulsoup4` — HTML 转纯文本 + 链接提取
- `requests` — HTTP 下载报告
- `python-dotenv` — 读取 .env 配置
- `openai` — 调用 DeepSeek API（兼容 OpenAI SDK）
- `markdown` / `pdfkit` — 预留
