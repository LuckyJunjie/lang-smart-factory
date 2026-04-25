# 部署文档

## 环境要求

- Python 3.9+
- Redis 6.0+
- Godot 4.0+ (仅游戏项目)

## 安装

```bash
# 克隆仓库
git clone https://github.com/LuckyJunjie/lang-smart-factory.git
cd lang-smart-factory

# 安装依赖
pip install -r requirements.txt
```

## 配置

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env`:
```
LLM_MODEL=gpt-4
OPENAI_API_KEY=your-api-key-here
REDIS_URL=redis://localhost:6379
SMART_FACTORY_API=http://192.168.3.75:5000
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/YOUR-WEBHOOK
PORT=5001
```

## 运行

### 启动 API 服务器
```bash
python api_server.py
# 访问 http://localhost:5001
```

### 启动 Worker
```bash
python workers/implementation_worker.py
```

### 使用 CLI
```bash
python cli.py run --requirement "实现股票筛选功能"
```

### 访问仪表盘
- API: http://localhost:5001/api/v1/health
- 监控: http://localhost:5001/dashboard/langflow

## Docker 部署 (可选)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "api_server.py"]
```

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/unit/ -v

# 运行集成测试
pytest tests/integration/ -v
```

## 项目结构

```
lang-smart-factory/
├── src/
│   ├── agents/          # AI Agent 实现
│   ├── workflows/       # 工作流定义
│   └── tools/          # 工具层
├── workers/            # Worker 实现
├── templates/          # 前端模板
├── tests/              # 测试
├── docs/               # 文档
├── api_server.py       # REST API
├── cli.py             # CLI 入口
└── requirements.txt   # 依赖
```
