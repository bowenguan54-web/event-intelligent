# 智能会议助手系统

## 技术栈
- **前端**: Vue 3 + Vite + Element Plus + Pinia + Vue Router
- **后端**: Python FastAPI + SQLAlchemy + WebSocket
- **数据库**: SQLite (开发) / PostgreSQL (生产)

## 项目结构
```
├── frontend/          # Vue3 前端项目
├── backend/           # FastAPI 后端项目
└── README.md
```

## 快速启动

### 后端
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

## 功能模块
1. 会议管理 - 创建、编辑、删除会议
2. 会议记录 - 实时语音转写与记录
3. 要点生成 - AI 自动提取会议要点
4. 纪要生成与审签 - AI 生成纪要 + 电子签名
5. 待办事项 - 任务分发与跟踪
6. 进度跟踪 - 甘特图与统计分析
7. 归档查询 - 全文/语义检索
