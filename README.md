# Dahzah 试剂/标准品管理模块

独立的质量检验试剂/标准品管理模块，可快速集成到任何 Dahzah 框架项目中。

## 功能特性

- 试剂/标准品台账管理（CRUD）
- AI 标签识别（支持 MiniMax VL 模型）
- 自动生成入场批号（格式：年月日9序号，如 260617901）
- Excel 批量导出
- 有效期管理
- 库存状态跟踪
- 多图片上传支持

## 模块结构

```
dahzah-reagent-module/
├── backend/                                    # 后端模块
│   ├── app/                                    # 应用骨架（集成时替换）
│   │   ├── __init__.py
│   │   ├── core/                              # 核心模块
│   │   │   ├── __init__.py
│   │   │   └── storage.py                     # 文件存储
│   │   ├── modules/                           # 业务模块
│   │   │   ├── __init__.py
│   │   │   └── quality/
│   │   │       ├── __init__.py
│   │   │       └── reagent_api.py             # API路由入口
│   │   └── platform/                          # 平台模块
│   │       ├── __init__.py
│   │       ├── database.py                   # 数据库会话
│   │       └── ai/                            # AI服务
│   │           ├── __init__.py
│   │           ├── service.py                  # AI日志服务
│   │           └── minimax_util.py            # MiniMax工具
│   ├── reagent_api.py                          # 试剂管理API路由
│   ├── reagent_service.py                      # 试剂业务逻辑
│   ├── reagent_schemas.py                      # Pydantic数据模型
│   ├── ai_config.py                            # AI配置管理
│   ├── ai_config_api.py                        # AI配置API
│   ├── ai_log_api.py                          # AI日志API
│   ├── ai/                                     # AI模块（独立实现）
│   │   ├── __init__.py
│   │   ├── models.py                          # AI日志模型
│   │   └── service.py                         # AI日志服务
│   ├── alembic/                               # 数据库迁移
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       ├── 20260609_0001_quality_reagent.py  # 试剂表迁移
│   │       └── 20260609_0003_ai_config.py        # AI配置表迁移
│   └── alembic.ini
├── frontend/                                  # 前端模块
│   └── src/
│       ├── actions/
│       │   └── quality-reagent.ts              # Server Actions
│       ├── app/
│       │   └── quality/
│       │       └── reagent/
│       │           └── page.tsx                # 试剂管理页面
│       └── types/
│           └── reagent-quality.ts              # 类型定义
└── README.md
```

## 快速集成

本模块设计了两种集成方式：

### 方式一：完整替换（推荐）

将 `backend/app/` 目录下的文件复制到主项目对应位置，覆盖占位符文件：

```bash
# 复制应用骨架（核心依赖）
cp -r backend/app/platform/ai/* 你的后端路径/app/platform/ai/
cp backend/app/platform/database.py 你的后端路径/app/platform/
cp backend/app/core/storage.py 你的后端路径/app/core/

# 复制试剂管理模块
cp backend/reagent_api.py 你的后端路径/app/modules/quality/
cp backend/reagent_service.py 你的后端路径/app/modules/quality/
cp backend/reagent_schemas.py 你的后端路径/app/modules/quality/

# 复制 AI 配置相关文件
cp backend/ai_config.py 你的后端路径/app/modules/quality/
cp backend/ai_config_api.py 你的后端路径/app/modules/v1/
cp backend/ai_log_api.py 你的后端路径/app/modules/v1/
cp -r backend/ai/* 你的后端路径/app/modules/ai/

# 复制数据库迁移脚本
cp backend/alembic/versions/* 你的后端路径/alembic/versions/
```

### 方式二：独立模块运行

后端已内置完整的 `app/` 骨架，可直接运行：

```bash
cd backend
uv sync
uv run uvicorn app.modules.quality.reagent_api:router --reload
```

---

### 一、后端集成

#### 1.1 注册路由

编辑主项目的路由注册文件（通常是 `app/api/v1/api.py` 或 `app/main.py`）：

```python
from fastapi import APIRouter
from app.modules.quality.reagent_api import router as reagent_router
from app.ai_config_api import router as ai_config_router
from app.ai_log_api import router as ai_log_router

# 在主 API router 中注册
api_router = APIRouter()
api_router.include_router(reagent_router, prefix="/quality", tags=["质量检验-试剂管理"])
api_router.include_router(ai_config_router)
api_router.include_router(ai_log_router)
```

#### 1.2 运行数据库迁移

```bash
cd 你的后端项目
uv run alembic upgrade head
```

#### 1.3 配置环境变量

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dahzah

# MiniMax AI (AI标签识别功能需要)
MINIMAX_API_KEY=your_api_key
MINIMAX_BASE_URL=https://api.minimax.chat
MINIMAX_MODEL=MiniMax-VL-01
```

---

### 二、前端集成

#### 2.1 复制文件

```bash
# 复制页面组件
cp -r frontend/src/app/quality 你的前端路径/src/app/\(dashboard\)/quality/

# 复制 Server Actions
cp frontend/src/actions/quality-reagent.ts 你的前端路径/src/actions/

# 复制类型定义
cp frontend/src/types/reagent-quality.ts 你的前端路径/src/types/
```

#### 2.2 添加菜单配置

编辑 `src/lib/menu-config.ts`，在质量模块菜单中添加：

```typescript
{
  key: "reagent-quality",
  label: "试剂/标准品管理",
  path: "/quality/reagent"
}
```

#### 2.3 配置环境变量

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## API 接口

### 试剂管理 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /quality/reagent/list | 获取试剂列表（支持分页、关键词搜索） |
| GET | /quality/reagent/{id} | 获取试剂详情 |
| POST | /quality/reagent | 创建试剂记录 |
| PUT | /quality/reagent/{id} | 更新试剂记录 |
| DELETE | /quality/reagent/{id} | 删除试剂记录 |
| POST | /quality/reagent/recognize | AI 识别试剂标签图片 |
| GET | /quality/reagent/next-lot-no | 获取下一个入场批号 |
| GET | /quality/reagent/export | 导出试剂台账 Excel |

### AI 配置 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/ai-config/ | 获取AI配置 |
| POST | /api/v1/ai-config/ | 更新AI配置 |
| GET | /api/v1/ai-config/status | 获取AI服务状态 |
| POST | /api/v1/ai-config/test | 测试AI连接 |

### AI 日志 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/v1/ai-logs/ | 获取AI日志列表 |
| GET | /api/v1/ai-logs/{id} | 获取日志详情 |
| POST | /api/v1/ai-logs/ | 创建日志记录 |
| GET | /api/v1/ai-logs/stats/summary | 获取AI使用统计 |
| DELETE | /api/v1/ai-logs/{id} | 删除日志记录 |
| DELETE | /api/v1/ai-logs/cleanup | 清理旧日志 |

---

## 数据库表结构

### qms_reagent_quality

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | UUID | 主键 |
| reagent_label_urls | TEXT[] | 试剂标签图片URL数组 |
| reagent_name | VARCHAR(200) | 试剂名称 |
| arrival_date | DATE | 到货日期 |
| production_date | DATE | 生产日期 |
| lot_no | VARCHAR(100) | 批号 |
| incoming_lot_no | VARCHAR(100) | 入场批号 |
| expiration_date | DATE | 有效期 |
| specification | VARCHAR(100) | 规格 |
| category | VARCHAR(50) | 分类（reagent/standard/reference/consumable） |
| reagent_no | VARCHAR(100) | 编号 |
| content | VARCHAR(100) | 含量/纯度 |
| manufacturer | VARCHAR(200) | 生产厂家 |
| quantity | DECIMAL(10,2) | 数量 |
| unit | VARCHAR(20) | 单位 |
| status | VARCHAR(20) | 状态 |
| created_by | VARCHAR(100) | 创建人 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## AI 配置表结构

### qms_ai_config

AI功能全局配置表，存储在 `qms` schema 下。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | SERIAL | 主键 |
| key | VARCHAR(100) | 配置键名 |
| value | TEXT | 配置值(JSON格式) |
| description | TEXT | 配置描述 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### qms_ai_log

AI交互日志表，记录所有AI功能的调用。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | SERIAL | 主键 |
| user_id | VARCHAR(100) | 用户ID |
| session_id | VARCHAR(100) | 会话ID |
| module | VARCHAR(50) | 模块名称 |
| action | VARCHAR(50) | 操作类型 |
| prompt | TEXT | 发送的提示词 |
| response | TEXT | AI响应内容 |
| model | VARCHAR(100) | 使用的模型 |
| tokens_used | INTEGER | 使用的token数 |
| status | VARCHAR(20) | 状态(success/failed) |
| error_message | TEXT | 错误信息 |
| request_params | JSONB | 请求参数 |
| response_time | INTEGER | 响应时间(毫秒) |
| created_at | TIMESTAMP | 创建时间 |

### AI 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| enabled | boolean | false | 是否启用AI功能 |
| api_key | string | - | API密钥 |
| base_url | string | - | API基础URL |
| model | string | MiniMax/VL-01 | 模型名称 |
| max_tokens | integer | 2048 | 最大token数 |
| temperature | float | 0.7 | 温度参数 |
| prompt_template | string | - | 通用提示词模板 |
| image_analysis_prompt | string | - | 图片分析提示词 |
| label_recognition_prompt | string | - | 标签识别提示词 |

---

## 状态说明

| 状态值 | 说明 |
|--------|------|
| available | 可用 |
| low_stock | 库存不足 |
| expired | 已过期 |
| quarantine | 待检 |
| scrap | 报废 |

---

## 分类说明

| 分类值 | 说明 |
|--------|------|
| reagent | 试剂 |
| standard | 标准品 |
| reference | 对照品 |
| consumable | 耗材 |

---

## 单位选项

- g (克)
- kg (千克)
- mg (毫克)
- mL (毫升)
- L (升)
- 支
- 瓶
- 盒

---

## AI 标签识别

模块支持通过 MiniMax VL 模型识别试剂标签图片，自动提取：
- 试剂名称
- 批号
- 生产厂家
- 生产日期
- 有效期
- 含量/纯度
- 规格

### AI 识别提示词

提示词已内置在 `reagent_service.py` 的 `SYSTEM_PROMPT_REAGENT_LABEL` 常量中，可根据需要调整。

---

## 依赖说明

### 后端依赖

```toml
# pyproject.toml
fastapi>=0.100.0
sqlalchemy>=2.0.0
asyncpg>=0.28.0
pydantic>=2.0.0
openpyxl>=3.1.0
```

### 前端依赖

```json
{
  "antd": "^6.4.3",
  "@ant-design/icons": "^6.2.3",
  "dayjs": "^1.11.0"
}
```

---

## 注意事项

1. **数据库 Schema**：表创建在 `qms` schema 下
2. **图片存储**：使用本地文件系统，存放在 `uploads/reagent-labels/` 目录
3. **入场批号格式**：年月日9序号，如 `260617901` 表示 2026年6月17日第1个
4. **AI 功能**：可选功能，不配置 MiniMax API Key 时无法使用

---

## License

MIT
