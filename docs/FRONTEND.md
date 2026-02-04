# MathVideo 前后端开发指南

## 📂 目录结构

```
mathvideo/
├── backend/                    # FastAPI 后端
│   ├── main.py                # 应用入口
│   ├── api/
│   │   ├── projects.py        # 项目管理 API
│   │   ├── generate.py        # 生成任务 API + WebSocket
│   │   └── refiner.py         # 视觉优化 API
│   └── requirements.txt
├── frontend/                   # Next.js 前端
│   ├── app/
│   │   ├── page.tsx           # 首页
│   │   ├── layout.tsx         # 根布局
│   │   ├── globals.css        # 全局样式
│   │   └── projects/
│   │       └── [slug]/
│   │           └── page.tsx   # 项目详情页
│   ├── components/
│   │   ├── GenerateForm.tsx   # 生成表单
│   │   ├── LogViewer.tsx      # 实时日志
│   │   ├── VideoPlayer.tsx    # 视频播放器
│   │   ├── StoryboardEditor.tsx # 故事板编辑器
│   │   ├── ProjectList.tsx    # 项目列表
│   │   └── RefinerPanel.tsx   # 视觉优化面板
│   ├── lib/
│   │   └── api.ts             # API 客户端
│   └── package.json
├── mathvideo/                  # 核心逻辑包
├── output/                     # 生成的项目
└── start-dev.sh               # 开发环境启动脚本
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 后端依赖
pip install -r backend/requirements.txt

# 前端依赖
cd frontend
npm install
```

### 2. 启动开发服务器

**方式一：使用启动脚本**

```bash
# 终端 1 - 启动后端
./start-dev.sh backend

# 终端 2 - 启动前端
./start-dev.sh frontend
```

**方式二：手动启动**

```bash
# 终端 1 - 后端 (端口 8000)
python -m uvicorn backend.main:app --reload --port 8000

# 终端 2 - 前端 (端口 3000)
cd frontend && npm run dev
```

### 3. 访问应用

- **前端界面**: http://localhost:3000
- **API 文档**: http://localhost:8000/docs
- **API 健康检查**: http://localhost:8000/health

## 🔌 API 端点

### 项目管理

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/projects/` | 获取项目列表 |
| GET | `/api/projects/{slug}` | 获取项目详情 |
| DELETE | `/api/projects/{slug}` | 删除项目 |
| GET | `/api/projects/{slug}/storyboard` | 获取 Storyboard |
| PUT | `/api/projects/{slug}/storyboard` | 更新 Storyboard |
| GET | `/api/projects/{slug}/videos` | 获取视频列表 |
| GET | `/api/projects/{slug}/scripts` | 获取脚本列表 |

### 生成任务

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/generate/` | 启动生成任务（支持文本与图片输入） |
| WebSocket | `/api/generate/ws/{task_id}` | 实时日志推送 |

### 视觉优化

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/refiner/{slug}/critique/{section_id}` | 视觉分析 |
| POST | `/api/refiner/{slug}/refine` | 代码优化 |
| POST | `/api/refiner/{slug}/render/{section_id}` | 重新渲染 |

## 🎨 前端技术栈

- **框架**: Next.js 14 (App Router)
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **图标**: Lucide React
- **代码编辑器**: Monaco Editor (可选)

## 🔧 开发注意事项

### 前端代理配置

前端通过 `next.config.js` 代理 API 请求到后端：

```js
async rewrites() {
  return [
    { source: '/api/:path*', destination: 'http://localhost:8000/api/:path*' },
    { source: '/static/:path*', destination: 'http://localhost:8000/static/:path*' },
  ];
}
```

### CORS 配置

后端已配置 CORS 允许前端跨域访问：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 静态文件服务

后端将 `output/` 目录挂载为静态文件服务：

- 访问路径: `/static/{项目slug}/media/videos/...`
- 例如: `/static/勾股定理/media/videos/section_1/480p15/Section1Scene.mp4`

## 📝 常见问题

### Q: 前端无法连接后端？

确保后端服务器正在运行（端口 8000），检查终端是否有错误信息。

### Q: WebSocket 连接失败？

WebSocket 使用直连地址 `ws://localhost:8000`，不经过 Next.js 代理。确保后端正在运行。

### Q: 视频无法播放？

1. 检查视频文件是否存在于 `output/{slug}/media/videos/` 目录
2. 检查浏览器控制台是否有 CORS 错误
3. 确认后端静态文件服务已正确挂载
