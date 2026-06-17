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
│   ├── reagent_api.py                          # API 路由
│   ├── reagent_service.py                       # 业务逻辑
│   ├── reagent_schemas.py                      # 数据模型
│   └── 20260609_0001_quality_reagent.py        # 数据库迁移脚本
├── frontend/                                   # 前端模块
│   └── src/
│       ├── actions/
│       │   └── quality-reagent.ts               # Server Actions
│       ├── app/
│       │   └── quality/
│       │       └── reagent/
│       │           └── page.tsx                # 试剂管理页面
│       └── types/
│           └── reagent-quality.ts               # 类型定义
└── README.md                                  # 本文件
```

## 快速集成

### 一、后端集成

#### 1.1 复制文件

```bash
# 复制 API 文件到你的后端项目
cp reagent_api.py 你的后端路径/app/modules/quality/
cp reagent_service.py 你的后端路径/app/modules/quality/
cp reagent_schemas.py 你的后端路径/app/modules/quality/

# 复制数据库迁移脚本
cp 20260609_0001_quality_reagent.py 你的后端路径/alembic/versions/
```

#### 1.2 注册路由

编辑 `app/modules/__init__.py`，添加：

```python
from .quality.reagent_api import router as reagent_router
```

编辑 `app/api/v1/api.py` 或 `app/modules/quality/__init__.py`：

```python
from fastapi import APIRouter
from app.modules.quality.reagent_api import router as reagent_router

router = APIRouter()
router.include_router(reagent_router, prefix="/quality", tags=["质量检验-试剂管理"])
```

#### 1.3 运行数据库迁移

```bash
cd 你的后端项目
uv run alembic upgrade head
```

#### 1.4 配置环境变量

```env
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
