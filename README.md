# IECS · 电商智能客服后端

一套基于 **LLM + 规则引擎** 混合架构的电商智能客服系统后端，以对话交互为核心，
帮助电商平台用户完成**订单查询、物流追踪、退款申请、商品咨询、相似商品推荐**等日常客服场景。

> **项目定位**：本仓库是整套电商智能客服系统中「智能客服后端」模块的实现，从 0 手写完成。
> 智能客服前端与原生电商业务后端不在本仓库范围内，详见「系统组成」。

## 功能概览

系统把每一轮用户输入归入三类能力之一，互斥路由：

| 能力类型 | 说明 | 典型场景 |
| --- | --- | --- |
| 任务流程 Task | 步骤稳定、需逐步收集信息并执行动作的业务任务 | 申请退款、查订单状态、查物流 |
| 信息检索 Knowledge | 先检索可信信息，再由 LLM 组织成自然语言回答 | 商品信息、退款政策、配送规则 |
| 闲聊 Chitchat | 不属于明确任务、也不适合知识检索时的兜底 | 打招呼、寒暄、模糊输入 |

**主要功能**

| 功能 | 说明 |
| --- | --- |
| 订单状态查询 | 用户提供订单号 → 调用商城 API 查询 → 回复订单状态 |
| 物流追踪 | 用户提供订单号 → 查询物流轨迹 → 回复物流进度 |
| 退款申请 | 收集订单号 + 退款原因 → 提交退款申请 |
| 商品信息咨询 | 用户发送商品对象 → 查询商品详情 → LLM 自然回复 |
| 相似商品推荐 | 基于当前商品 → 推荐类似商品 |
| 闲聊兜底 | 无法匹配任务 / 知识轨道时，由 LLM 自然闲聊 |

### 任务流程示例

```text
用户：我想申请退款
客服：请发送你要退款的订单。
用户：[退款订单]
客服：请简单说一下退款原因。
用户：尺码不合适
客服：好的，订单 A20240315001 的退款申请已提交，原因是：尺码不合适。后续会尽快为你处理。
```

### 信息检索：知识意图与检索方式

不同类型的问题检索方式并不相同——核心思路不是让模型自由回答，而是先找到可信的信息来源：

| 知识意图 | 检索方式 | 示例问题 |
| --- | --- | --- |
| 商品信息咨询 | 业务 API | “这件商品是什么材质？” |
| 订单信息咨询 | 业务 API | “这个订单现在是什么情况？” |
| 退款 / 退货政策咨询 | FAQ | “退款政策是怎样的？” |
| 配送政策咨询 | FAQ | “多久发货？包邮吗？” |
| 平台规则咨询 | 知识库 | “平台有哪些限制规则？” |
| 通用电商问题 | FAQ / 知识库 | “优惠券怎么用？” |

```text
用户：这件商品大概是什么情况？
客服：这件商品的名称是“轻薄连帽防晒衣”，当前价格为 129 元，库存状态为有货。
      如果你想进一步了解规格参数或售后信息，也可以继续问我。

用户：适合什么季节穿？
客服：从商品名称和描述来看，这是一件偏轻薄款的防晒衣，更适合春夏季节或日常通勤、户外防晒场景使用。
```

### 闲聊示例

```text
用户：你好
客服：你好，这里是电商助手。我可以帮你查订单状态、查物流、了解商品信息，或者提交退款申请。

用户：你还挺聪明
客服：谢谢夸奖。如果你有订单、物流或者商品相关的问题，我都可以继续帮你看一下。
```

## 核心设计

- **LLM+规则双引擎**：LLM 负责意图识别与自然语言生成，YAML 规则引擎负责业务流程控制，兼顾灵活性与可靠性。
- **三轨道并行设计**：每一轮对话被分类为**任务（task）/ 知识问答（knowledge）/ 闲聊（chitchat）**三轨道之一，互斥路由，确保精准调度。
- **YAML驱动流程**：所有业务流程（订单查询、物流追踪等）和系统流程（信息收集、澄清、打断等）均用 YAML 定义，配置直观、无需改代码即可调整对话策略，后续还可提供可视化流程配置界面。
- **有状态对话**：完整对话上下文序列化为 JSON 持久化到 MySQL，支持跨会话恢复。

## 系统组成

| 子模块 | 端口 | 角色 | 是否在本仓库 |
| --- | --- | --- | --- |
| `customer-service-backend` | 18082 | 智能客服对话引擎（本仓库核心） | 是 |
| `customer-service-frontend` | 5173 | 客服聊天界面（Vue 3 + Vite） | 否 |
| `ecommerce-service-backend` | 18081 | 电商业务 Mock 接口（业务数据提供方） | 否 |
| MySQL 8.4 | 3306 | 对话状态与业务数据存储 | 否（Docker 编排） |

## 设计文档

### 项目设计理念

<!-- TODO: 上传「项目设计理念」图，或替换下方路径 -->
<img width="2377" height="809" alt="image" src="https://github.com/user-attachments/assets/b53a9ae1-6918-4017-b36d-2f09f0eed948" />


### 系统整体架构

> 智能客服系统构建在原生电商业务系统之上，复用其用户、订单等业务数据，
> 自身只负责对话编排与客服侧状态持久化。图中左侧的电商前端为传统电商业务，非本项目开发重点。

<!-- TODO: 上传「系统整体架构」图，或替换下方路径 -->
<img width="2314" height="746" alt="image" src="https://github.com/user-attachments/assets/568e47d4-505a-43a7-9b79-636efa29d657" />


### 智能客服后端分层设计

智能客服后端自上而下分为五层，各层职责单一、依赖单向：

| 层次 | 主要职责 |
| --- | --- |
| API 层 | 定义对话处理接口，接收 HTTP 请求，组织请求与响应 |
| Service 层 | 串起一次对话处理：查询用户对话状态 → 调用对话引擎处理 → 存储对话状态 |
| Engine 层 | 对话处理的顶层调度，决定走哪条处理轨道 |
| Handler 层 | 按用户消息意图，执行不同轨道的消息处理 |
| Repository 层 | 状态存储、数据库、模型与 HTTP 能力 |

Engine 层的核心组件：

- `TurnPlanner`：负责本轮规划
- `TurnPlanValidator`：意图判断与校验
- `TaskHandler`：负责固定任务流推进
- `KnowledgeHandler`：负责信息检索与回答
- `ChitchatHandler`：负责闲聊与兜底回复
- `ClarifyResponder`：用户问题的澄清处理

<!-- TODO: 上传「智能客服后端分层设计」图，或替换下方路径 -->
<img width="2457" height="891" alt="image" src="https://github.com/user-attachments/assets/0c7f3ceb-f477-48ae-a6cb-4b7c65bbe972" />


> 当前代码已落地 `conf`（配置）与 `infrastructure`（LLM / HTTP / 数据库基础设施），
> 其余分层将逐步补齐。

## 技术栈

| 方向 | 选型 |
| --- | --- |
| 语言 / 包管理 | Python >= 3.11、[uv](https://docs.astral.sh/uv/) |
| Web 框架 | FastAPI |
| 大模型接入 | LangChain（`init_chat_model`，OpenAI 兼容接口） |
| 数据访问 | SQLAlchemy 2.x（异步）+ aiomysql |
| 异步 HTTP | httpx |
| 配置管理 | pydantic-settings（`.env` 驱动） |
| Prompt 模板 | Jinja2 |
| 流程配置 | YAML |

## 目录结构

```
.
├── main.py                  # 项目入口（FastAPI app 接入中）
├── pyproject.toml           # 项目元信息与依赖声明
├── uv.lock                  # 依赖版本锁定，请勿手改
├── .env.example             # 配置模板
├── docs/images/             # README 设计图存放目录
└── banban/
    ├── conf/config.py       # 全局配置单例 settings
    ├── infrastructure/
    │   ├── ai_clients.py    # LLM 客户端单例 llm_client
    │   ├── database.py      # 异步引擎 engine 与会话工厂 session_factory
    │   └── http_util.py     # 异步 HTTP 客户端单例 http_client
    └── test/                # 冒烟脚本（见「本地验证」）
```

## 快速开始

### 前置依赖

| 依赖 | 版本 / 地址 | 说明 |
| --- | --- | --- |
| Python | >= 3.11 | 由 uv 自动管理虚拟环境 |
| MySQL | 8.x | 建库 `customer_service`，字符集 `utf8mb4` |
| 电商业务后端 | `http://127.0.0.1:18081` | 提供订单、物流、商品等业务数据 |

### 1. 安装 uv

```bash
# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

uv --version      # 能输出版本号即安装成功
```

### 2. 拉取代码并安装依赖

```bash
git clone https://github.com/banban0312/iecs.git
cd iecs
uv sync
```

### 3. 配置环境变量

```bash
cp .env.example .env      # Windows PowerShell: Copy-Item .env.example .env
```

`.env` 已被 gitignore，不会入库。配置项说明：

| 变量 | 说明 | 示例 |
| --- | --- | --- |
| `LLM_MODEL` | 模型名称 | `deepseek-flash` |
| `LLM_BASE_URL` | 模型服务地址（需 OpenAI 兼容） | `https://api.deepseek.com` |
| `LLM_API_KEY` | 模型服务密钥 | 自行填写 |
| `COMMERCE_API_BASE_URL` | 电商业务后端地址 | `http://127.0.0.1:18081` |
| `DATABASE_URL` | 异步数据库连接串 | `mysql+aiomysql://<用户>:<密码>@127.0.0.1:3306/customer_service?charset=utf8mb4` |
| `APP_HOST` / `APP_PORT` | 服务监听地址与端口 | `127.0.0.1` / `18082` |

> 任何提供 OpenAI 兼容接口的模型服务都可以直接替换 `LLM_BASE_URL` / `LLM_MODEL`。

### 4. 启动服务

```bash
uv run python main.py
```

启动后访问接口文档：<http://127.0.0.1:18082/docs>

> **注意**：FastAPI 应用入口尚未接入（`main.py` 目前仍是初始模板）；
> 现阶段请先用下方「本地验证」逐个确认各层依赖已打通。

### 5. 常用 uv 命令

| 命令 | 作用 |
| --- | --- |
| `uv sync` | 按 `pyproject.toml` + `uv.lock` 同步依赖到 `.venv` |
| `uv add <包名>` | 添加依赖并更新锁文件 |
| `uv run <命令>` | 在项目虚拟环境中运行命令，无需手动激活 |
| `uv pip list` | 查看已安装的依赖 |
| `uv remove <包名>` | 移除依赖 |

## 本地验证

以下脚本按层验证环境是否打通，请按依赖顺序执行：

```bash
uv run python -m banban.test.test_settings     # 1. 配置能否加载
uv run python -m banban.test.test_ai_clients   # 2. LLM 能否调通（需有效 API Key）
uv run python -m banban.test.test_database     # 3. MySQL 能否连通（需先启动数据库）
uv run python -m banban.test.test_http_util    # 4. 业务后端能否调通（需先启动业务后端）
```

> 这些是手写冒烟脚本，**不是 pytest 用例**，请用上面的方式逐条运行。

## 依赖的外部接口

客服后端通过 HTTP 调用电商业务后端获取业务事实，当前约定的接口如下：

| 接口 | 作用 |
| --- | --- |
| `GET /users/{user_id}/orders` | 获取某用户最近订单列表 |
| `GET /users/{user_id}/products` | 获取某用户最近商品列表 |
| `GET /orders/{order_id}` | 获取订单详情 |
| `GET /orders/{order_id}/status` | 获取订单状态 |
| `GET /orders/{order_id}/logistics` | 获取物流信息 |
| `GET /products/{product_id}` | 获取商品详情 |
| `POST /orders/{order_id}/shipping-reminders` | 创建催发货提醒 |
| `POST /orders/{order_id}/refund-applications` | 创建退款申请 |

本服务对外暴露的接口（规划）：

| 路径前缀 | 说明 |
| --- | --- |
| `/api/*` | 对话消息、历史消息查询 |
| `/health/*` | 健康检查 |
