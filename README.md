# OpenRouterAvsB

在 OpenRouter 上选两个模型，并排看它们的 benchmark 数据怎么比。表格、雷达图、柱状图三种视图，数据全是实时拉的，不缓存。

## 结构

后端 FastAPI，前端 Vue 3 + TypeScript。

```
OpenRouterAvsB/
├── server/                  # FastAPI 后端 (Python 3.12)
│   ├── main.py              # API 路由
│   ├── scraper.py           # 异步抓取 OpenRouter 数据
│   ├── models.py            # Pydantic 数据模型
│   └── config.py            # API 地址、并发设置
├── web/                     # Vue 3 前端 (Vite + TypeScript)
│   └── src/
│       ├── components/
│       │   ├── ModelSelector.vue    # 双模型选择器
│       │   ├── TableView.vue        # 表格对比
│       │   ├── RadarView.vue        # 雷达图
│       │   ├── BarView.vue          # 柱状图
│       │   ├── BenchmarkContent.vue # 视图容器
│       │   ├── NavBar.vue
│       │   └── FooterBar.vue
│       ├── composables/
│       │   ├── useState.ts          # 响应式状态管理
│       │   └── useBenchmarks.ts     # 数据请求调度
│       └── types/
│           └── index.ts             # 共享类型和常量
├── models.txt               # 模型 ID 列表
├── requirements.txt
└── run.bat                  # 一键启动（Windows）
```

## 启动

### 依赖

- Python 3.12+
- Node.js 18+

```bash
pip install -r requirements.txt
cd web && npm install
```

### 运行

```bash
# Windows 下一键启动
run.bat

# 或者分两个终端
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
cd web && npm run dev
```

前端跑在 `http://localhost:5173`，开发模式下 `/api` 请求自动转发到后端 8000 端口。

### 构建前端

```bash
cd web && npm run build
```

产物在 `web/dist/`，配合后端一起部署。

## API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/models` | 列出所有模型的基本信息 |
| GET | `/api/benchmarks` | 拉取全部模型的 benchmark 数据 |
| GET | `/api/benchmarks/{model_id}` | 拉取单个模型的 benchmark 数据 |

## 数据来源

全部实时从 OpenRouter 拉取，不做本地缓存。

- **模型信息**: `openrouter.ai/api/v1/models`（名称、定价、上下文长度）
- **AA 基准测试**: OpenRouter 内部 API（AA 指数、GPQA Diamond、HLE 等）
- **设计竞技场**: OpenRouter 内部 API（Elo 评分、胜率）

要比较哪些模型，写在 `models.txt` 里，一行一个 ID。后端启动时会自动排序。

## 数据流

1. 页面加载后先拉 `/api/models`，只拿模型元信息
2. 用户选中模型后再拉 `/api/benchmarks/{model_id}`，拿完整 benchmark
3. 已加载的 benchmark 缓存在响应式状态里，避免重复请求
4. 三种视图（表格、雷达图、柱状图）共用同一份数据

## 配色

- 模型 A: `#6fa3a7`（青灰）
- 模型 B: `#e8a882`（暖杏色）

所有视图组件统一使用这套颜色。
