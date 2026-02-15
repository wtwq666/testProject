# 智能数据分析助理 (SmartDataAssistant)

基于 Kimi 大模型 + LangChain + FastAPI 后端与 React 前端，支持自然语言查询 SQLite、实时可视化与会话管理。

## 技术栈

- **后端**: FastAPI, LangChain, SQLAlchemy, SQLite
- **前端**: React 18, TypeScript, Vite, Ant Design, ECharts, Zustand
- **大模型**: 月之暗面 Kimi

## 环境要求

- Python 3.11+（推荐 Conda）
- Node.js 18+
- （可选）已配置 [Linear](https://linear.app) 与 [task-manager 规则](.cursor/rules/task-manager.mdc) 用于任务同步

## 快速开始

### 1. Conda 环境与后端

```bash
# 创建环境（仅首次）
conda create -n smart-data python=3.11 -y
conda activate smart-data

# 安装依赖（在项目根目录）
pip install -r backend/requirements.txt

# 可选：使用清华镜像
# pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 初始化数据库与示例数据

```bash
cd backend
python -c "from app.database.seed import run_seed; run_seed()"
```

或从项目根目录（需先 `cd backend` 再执行）：

```bash
cd backend && python -m app.database.seed
```

（若项目路径含中文导致编码错误，可在资源管理器中进入 `backend` 文件夹，在该目录打开终端再执行上述命令。）

### 3. 启动后端

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

- 健康检查: http://localhost:8000/health  
- API 文档: http://localhost:8000/docs  

### 4. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问 http://localhost:5173 ，前端会通过 Vite 代理将 `/api` 请求转发到 `http://localhost:8000`。

## 项目结构

```
SmartDataAssistant/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py   # 入口、CORS、/health
│   │   ├── config.py
│   │   ├── database/ # 业务库 + 会话库 ORM 与 seed
│   │   ├── api/      # Phase3 起使用
│   │   └── services/
│   ├── data/         # SQLite 文件目录
│   └── requirements.txt
├── frontend/         # Vite + React + TS
│   ├── src/
│   └── vite.config.ts  # proxy /api -> 8000
├── .cursor/
│   ├── plans/       # 开发计划
│   └── rules/       # 任务管理规则（Linear 同步）
└── README.md
```

## 配置

- 后端环境变量见 `backend/.env.example`，复制为 `backend/.env` 并填写 `KIMI_API_KEY` 等。
- Linear 与 GitHub 在 `.cursor/rules/task-manager.mdc` 的配置区修改。

## 开发阶段

- **Phase1**（当前）: 基础框架、前后端可运行、数据库与示例数据就绪  
- **Phase2**: 前端三栏 UI（会话 / 问答 / 图表）  
- **Phase3**: 后端会话管理、Kimi、SQL Agent、SSE 流式  
- **Phase4**: 前后端联调与体验优化  

## License

MIT
