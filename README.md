# RAG 系统 - 蒲仙话方言智能问答系统

一个基于 RAG（检索增强生成）技术的智能问答系统，专门用于蒲仙话方言知识库查询和对话。系统集成了向量数据库、Elasticsearch 和本地 LLM 模型，支持知识库管理和智能对话功能。

## 系统架构

- **后端**: Flask + MySQL + ChromaDB + Elasticsearch
- **前端**: Vue 3 + Vite
- **AI模型**: Ollama (DeepSeek-R1) + BGE 嵌入模型
- **容器化**: Docker Compose

## 功能特性

- 🤖 智能对话：基于本地 LLM 的自然语言对话
- 📚 知识库管理：支持创建、上传、处理和删除知识库
- 🔍 RAG 检索：结合向量搜索和关键词搜索的混合检索
- 🗣️ 方言专家：专门的蒲仙话方言知识问答
- 📄 PDF 处理：自动提取和索引 PDF 文档内容
- 👤 用户认证：基于 Session 的用户登录系统

## 环境要求

- Docker & Docker Compose（包含所有依赖服务、后端、前端、Ollama）

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd rag
```

### 2. 配置环境变量

```bash
# 复制环境变量模板文件
cp .env.example .env
# 编辑 .env 文件，配置您的 API 密钥
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. 一键启动所有服务（推荐）

```bash
docker-compose up --build -d
```

此命令会自动启动：
- MySQL
- Elasticsearch
- Ollama
- Flask 后端
- Vue 前端

前端服务默认在 `http://localhost:5173`，后端服务在 `http://localhost:5000`。

---

### 4. 拉取 Ollama 本地模型（首次启动后执行）

Ollama 容器首次启动后，需要手动拉取 deepseek-r1:8b 模型：

```bash
# 确认 ollama 服务已启动
sudo docker compose up -d ollama
# 拉取模型（可实时看到进度）
sudo docker exec ollama ollama pull deepseek-r1:8b
```

如需查看已下载模型：
```bash
sudo docker exec ollama ollama list
```

> ⚠️ 不建议在 Dockerfile 或 build 阶段拉取模型，否则构建过程会极慢且无进度显示，且每次重建镜像都需重新下载。

如需关闭服务：
```bash
docker-compose down
```

如需查看日志：
```bash
docker-compose logs
```

**注意**: `.env` 文件已被添加到 `.gitignore` 中，不会被提交到版本控制系统。

### 后端配置 (`app/config.py`)

```python
class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://myuser:mypassword@localhost:3306/mydatabase"
    SECRET_KEY = '123456'  # 用于启用 session 和 cookie 的加密

    # DeepSeek API 配置（从环境变量读取）
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"

    # Ollama 配置
    OLLAMA_API_URL = "http://localhost:11434"
    OLLAMA_DEFAULT_MODEL = "deepseek-r1:8b"
    OLLAMA_DEFAULT_TEMPERATURE = 0.5

    # 向量数据库配置
    CHROMA_PERSIST_DIR = "./data/chroma"

    # Elasticsearch 配置
    ELASTICSEARCH_URL = "http://localhost:9200"

    # 知识库路径
    KNOWLEDGE_BASE_PATH = "./knowledge"
```

### 前端代理配置 (`frontend/vite.config.js`)

API 请求会自动代理到后端服务：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false,
      ws: true,
      rewrite: (path) => path
    }
  }
}
```

## 使用指南

### 1. 用户注册/登录

访问系统首页，点击注册或登录按钮创建账户。

### 2. 知识库管理

- **创建知识库**: 在知识库管理页面输入名称创建新知识库
- **上传文件**: 选择知识库并上传 PDF 文件
- **处理文件**: 点击处理按钮将文档内容索引到向量数据库
- **删除知识库**: 删除不需要的知识库及其所有文件

### 3. 智能对话

- **普通对话**: 与 AI 进行自然语言对话
- **知识库问答**: 选择特定知识库进行基于文档的问答
- **方言咨询**: 询问蒲仙话相关的方言知识

## 项目结构

```
├── app/                    # 后端应用
│   ├── routes/            # 路由模块
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── config.py          # 配置文件
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── components/    # Vue 组件
│   │   ├── views/         # 页面视图
│   │   └── api/           # API 接口
├── data/                  # 数据存储目录
├── knowledge/             # 知识库文件
├── models/                # AI 模型文件
├── .env                   # 环境变量配置（不提交到Git）
├── .env.example           # 环境变量模板
├── .gitignore             # Git忽略文件配置
├── docker-compose.yml     # Docker 配置
└── requirements.txt       # Python 依赖
```

## 开发说明

### 本地开发（可选）
如需在本地调试单独服务，可参考原有 app/Dockerfile、frontend/Dockerfile，或分别进入对应目录手动运行。

## 故障排除

### 常见问题

1. **API 密钥配置错误**
   - 确保已创建 `.env` 文件并配置了 `DEEPSEEK_API_KEY`
   - 检查 API 密钥是否有效
   - 确认 `.env` 文件在项目根目录

2. **Ollama 连接失败**
   - 确保 Ollama 服务容器已启动（docker-compose ps）
   - 检查模型是否已下载：`docker exec -it ollama ollama list`

3. **数据库连接错误**
   - 确保 Docker 服务正在运行：`docker-compose ps`
   - 检查数据库配置是否正确

4. **前端无法访问后端**
   - 检查后端服务是否在 5000 端口运行
   - 确认 Vite 代理配置正确

### 日志查看

```bash
# 查看 Docker 服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs mysql
docker-compose logs elasticsearch
```
