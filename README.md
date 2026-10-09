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
| 退款申请 | 收集订单号 + 退款原因 → 提交退款申请 → 按提交结果回复 |
| 商品信息咨询 | 用户发送商品对象 → 查询商品详情 → LLM 自然回复 |
| 相似商品推荐 | 基于当前商品 → 推荐类似商品 |
| 闲聊兜底 | 无法匹配任务 / 知识轨道时，由 LLM 自然闲聊 |
| 澄清与打断 | 意图不明确时反问澄清；任务进行中切换话题时自动挂起 / 恢复 |
| 历史会话 | 完整对话上下文持久化，支持跨会话恢复与历史消息查询 |

### 任务流程示例

```text
用户：我想申请退款
客服：请发送你要退款的订单。
用户：[退款订单]
客服：请简单说一下退款原因。
用户：尺码不合适
客服：好的，订单 A20240315001 的退款申请已提交，原因是：尺码不合适。后续会尽快为你处理。
```

若业务后端提交失败，则回复：

```text
客服：抱歉，订单 A20240315001 的退款申请提交失败，请联系人工客服。
```

### 信息检索：知识意图与检索方式

不同类型的问题检索方式并不相同——核心思路不是让模型自由回答，而是先找到可信的信息来源：

| 知识意图 | 检索方式 | 示例问题 |
| --- | --- | --- |
| 商品信息咨询 | 业务 API | “这件商品是什么材质？” |
| 订单信息咨询 | 业务 API | “这个订单现在是什么情况？” |
| 退款政策咨询 | 知识库（RAG） | “退款政策是怎样的？” |
| 退货政策咨询 | FAQ / 知识库 | “怎么退货？” |
| 配送政策咨询 | FAQ / 知识库 | “多久发货？包邮吗？” |
| 平台规则咨询 | 知识库（RAG） | “平台有哪些限制规则？” |
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

- **LLM + 规则双引擎**：LLM 负责意图识别与自然语言生成，YAML 规则引擎负责业务流程控制，兼顾灵活性与可靠性。
- **三轨道互斥路由**：每一轮对话被分类为**任务（task）/ 知识问答（knowledge）/ 闲聊（chitchat）**三轨道之一，由 `TurnPlan` 统一表达，`TurnPlanValidator` 校验后再分发。
- **YAML 驱动流程**：所有业务流程（订单查询、物流追踪、退款等）和系统流程（信息收集、澄清、打断、恢复等）均用 YAML 定义，配置直观、无需改代码即可调整对话策略。
- **有状态对话**：完整对话上下文（会话 / 轮次 / 任务上下文 / 槽位 / 聚焦对象）序列化为 JSON 持久化到 MySQL，支持跨会话恢复。
- **会话生命周期**：连续 2 小时无活动则关闭当前会话并重置运行时状态，下次输入开启新会话。
- **双通道接入**：同时提供 HTTP 与 WebSocket 两种对话接入方式，WebSocket 支持 `thinking / done` 处理状态推送。

## 系统组成

| 子模块 | 端口 | 角色 | 是否在本仓库 |
| --- | --- | --- | --- |
| `customer-service-backend` | 18082 | 智能客服对话引擎（本仓库核心） | 是 |
| `customer-service-frontend` | 5173 | 客服聊天界面（Vue 3 + Vite） | 否 |
| `ecommerce-service-backend` | 18081 | 电商业务 Mock 接口（业务数据提供方） | 否 |
| MySQL 8.x | 3306 | 对话状态与业务数据存储 | 否（Docker 编排） |

## 对话处理链路

一次文本消息的处理过程：

```text
HTTP/WebSocket 请求
  └─ API 层          组装 UserMessage，返回 ProcessResult
      └─ Service 层  加载 DialogueState → 调用 Engine → 回写状态
          └─ Engine 层
              ├─ 1. TurnPlanner          调用 LLM 生成本轮 TurnPlan
              ├─ 2. TurnPlanValidator    校验并归一化（非法则转澄清）
              └─ 3. 轨道分发
                    ├─ TaskHandler      → CommandProcessor → FlowExecutor → ActionRunner
                    ├─ KnowledgeHandler → Provider 检索 → LLM 组织回答
                    └─ ChitchatHandler  → LLM 闲聊
```

- 用户发送**对象消息**（订单 / 商品卡片）时，`DialogueEngine` 会先把对象写入 `focused_object`；
  若正处于收集槽位的系统任务中，则自动生成填槽指令直接喂给 `TaskHandler`。
- 任务轨道内部为三层协作：`CommandProcessor`（结构化命令 → 状态变更）、`FlowExecutor`（按 YAML 推进流程直到需要执行动作）、`ActionRunner`（执行 Action 并回写槽位）。

## 接口一览

### HTTP 接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `POST` | `/api/chat` | 发送一条消息，返回本轮客服回复 |
| `GET` | `/api/chat/history?sender_id=xxx` | 查询某用户的历史会话消息 |

### WebSocket 接口

| 路径 | 说明 |
| --- | --- |
| `/ws/chat` | 双向对话通道，支持处理状态推送 |

**客户端 → 服务端**

```json
{ "type": "message", "sender_id": "user_1", "text": "我要退款", "message_id": null, "object": null }
```

- `type` 为 `message` 时进入对话处理；为 `cancel` 时忽略该条消息。
- `text` 与 `object` 二选一：文本消息填 `text`，对象消息填 `object`（`{type,id,title,attributes}`）。

**服务端 → 客户端**（按顺序）

```json
{ "type": "status",      "sender_id": "user_1", "data": { "status": "thinking" } }
{ "type": "bot_message", "sender_id": "user_1", "message_id": "...", "data": { "text": "请告诉我你的订单号。", "object": null } }
{ "type": "status",      "sender_id": "user_1", "data": { "status": "done" } }
```

- 一条消息可能产生多条 `bot_message`（例如先回复再追问）。
- 收到非法 JSON 时返回 `{ "type": "error", "data": { "code": "INVALID_JSON", ... } }`。

> 接口文档：启动后访问 <http://127.0.0.1:18082/docs>

## 设计文档

### 项目设计理念

<img width="2377" height="809" alt="项目设计理念" src="https://github.com/user-attachments/assets/b53a9ae1-6918-4017-b36d-2f09f0eed948" />

### 系统整体架构

> 智能客服系统构建在原生电商业务系统之上，复用其用户、订单等业务数据，
> 自身只负责对话编排与客服侧状态持久化。图中左侧的电商前端为传统电商业务，非本项目开发重点。

<img width="2314" height="746" alt="系统整体架构" src="https://github.com/user-attachments/assets/568e47d4-505a-43a7-9b79-636efa29d657" />

### 智能客服后端分层设计

智能客服后端自上而下分层，各层职责单一、依赖单向：

| 层次 | 主要职责 |
| --- | --- |
| API 层 | 定义对话处理接口（HTTP / WebSocket），接收请求，组织请求与响应 |
| Service 层 | 串起一次对话处理：查询用户对话状态 → 调用对话引擎处理 → 存储对话状态 |
| Engine 层 | 对话处理的顶层调度：意图规划、命令校验、轨道分发 |
| Handler 层 | 按用户消息意图，执行不同轨道的消息处理 |
| Repository 层 | 状态存储、数据库、模型与 HTTP 能力 |

Engine 层的核心组件：

- `TurnPlanner`：调用 LLM 完成本轮规划，产出 `TurnPlan`
- `TurnPlanValidator`：意图判断与结构化命令校验
- `TaskHandler`：负责固定任务流推进
- `KnowledgeHandler`：负责信息检索与回答
- `ChitchatHandler`：负责闲聊与兜底回复
- `ClarifyResponder`：用户问题的澄清处理

<img width="2457" height="891" alt="智能客服后端分层设计" src="https://github.com/user-attachments/assets/0c7f3ceb-f477-48ae-a6cb-4b7c65bbe972" />

## 分层与模块设计（原型图）

下面按 **API 层 → Service 层 → Repository 层 → 领域层 → Engine 层 → 意图识别 → 任务轨道 → 知识轨道** 的顺序，逐层给出设计原型与说明。

### 1. API 层 · 接口定义

![API 层 · 接口定义](docs/images/01-api-layer.png)

- 前端所有请求统一经 `router` 分发：业务数据走 `/commerce/*`（转发到电商业务后端），客服对话走 `/api/*`。
- 客服后端对外只暴露两个 HTTP 接口：
  - `@router.get("/api/chat/history")`：进入对话界面时，用 `sender_id` 拉取该用户的历史会话列表。
  - `@router.post("/api/chat")`：处理用户消息。
- **请求体两种形态**（`text` 与 `object` 二选一）：

  ```json
  { "sender_id": "u1001", "text": "你好呀", "object": null, "message_id": "msg_001" }
  ```
  ```json
  {
    "sender_id": "u1001", "text": null, "message_id": "msg_002",
    "object": { "type": "order | product", "id": "A20260001", "title": "…", "attributes": {} }
  }
  ```

- **历史记录查询接口**：`GET /api/chat/history`，参数 `sender_id`（必填，用户 ID）；响应 `{sender_id, messages:[{role, text, object}]}`，其中 `role` 为 `user` / `bot`。
- **对话接口**：`POST /api/chat`，参数 `sender_id`（必填）、`text`、`object`、`message_id`（可空）；`object` 内含 `type`（`order|product`，必填）、`id`（订单 / 商品 ID，必填）、`title`、`attributes`；响应 `{sender_id, message_id, messages: list[object]}`，列表每项含 `text` 与 `msg_object`。

### 2. Service 层 · 交互模型与领域模型

![Service 层设计](docs/images/02-service-layer.png)

- **交互模型**：定义 API 层接口的参数与返回值结构（`ChatRequest` / `ChatResponse`），面向外部协议。
- **领域模型**：Service 层在业务处理过程中的数据结构（`UserMessage` / `ProcessResult` / `BotMessage`），面向内部逻辑。
- 一次请求的模型转换链：`ChatRequest(text|object)` → `UserMessage` →（`process_message`）→ `ProcessResult` → `ChatResponse(text|object)`，从而让 HTTP 协议与业务逻辑解耦。
- 关键类：`ChatRequest(sender_id, text, object: ChatObjectPayload|None, message_id)`、`UserMessage(sender_id, message_id, type, text, object)`、`ProcessResult(sender_id, message_id, messages: list[BotMessage])`、`BotMessage`。

### 3. Repository 层 · 用户状态存储

![Repository 层](docs/images/03-repository-layer.png)

`DialogueStateRepository` 负责对话状态的读写，对上层屏蔽存储细节：

- `load(sender_id) -> DialogueState`：按 `sender_id` 查询；有则把 `state_json` 反序列化为 `DialogueState` 返回；没有则构造一个全新的对话状态返回。
- `save(state: DialogueState)`：把状态序列化为 JSON；库中已存在则更新，不存在则插入。

存储落在 MySQL 客服库的单表：

| 字段 | 说明 |
| --- | --- |
| `sender_id` | 用户唯一标识（主键） |
| `state_json` | 完整对话状态 JSON |

### 4. 领域层 · DialogueState 数据结构

![DialogueState 数据结构](docs/images/04-dialogue-state-model.png)

`DialogueState` 记录 / 存储某一个用户的对话状态，是引擎推进流程的唯一依据：

| 字段 | 说明 |
| --- | --- |
| `sender_id` | 当前对话状态关联的用户 ID |
| `active_task: TaskContext \| None` | 当前用户正在执行的任务上下文 |
| `paused_tasks: list[TaskContext]` | 被挂起的任务上下文 |
| `active_system_task: SystemContext \| None` | 当前用户系统任务上下文 |
| `focused_object: FocusedObject \| None` | 当前对话的聚焦对象 |
| `sessions: list[Session]` | 用户会话记录 |
| `current_session_id: str` | 当前会话 ID |
| `pending_turn: Turn` | 当前正在进行的对话轮次（不参与持久化） |

配套模型：

- `TaskContext`：`flow_id` / `step_id` / `slots: dict[str, any]`。
- `SystemContext`（`flow_id` / `step_id`）及其子类：`StartedSystemContext`、`ResumedSystemContext`、`CannotHandleSystemContext`、`CollectSystemContext`、`InterruptedSystemContext`、`CanceledSystemContext`，对应系统流程的**启动 / 恢复 / 无法处理 / 信息收集 / 打断 / 取消**。
- `FocusedObject`：`type` / `id` / `title` / `attributes`。
- `Session`：`session_id` / `created_at` / `last_activity_at` / `closed_at` / `turns: list[Turn]`。
- `Turn`：`turn_id` / `input_message: UserMessage` / `assistant_messages: list[BotMessage]`。

> 右侧示例：`refund_request`（退款请求）流程步骤为 `start → ask_order_number → ask_reason → submit_refund_request → generate_response → end`；任务所需槽位由流程按需声明，例如 `query_order_status`、`refund_request`。

### 5. Engine 层 · 一轮对话的处理流程

![DialogueEngine 业务逻辑流程](docs/images/05-dialogue-engine-flow.png)

`DialogueEngine.process(user_message, state)` 处理一轮对话，共六个阶段：

1. **准备会话**：按 `current_session_id` 取当前会话；不存在或已过期则开启新会话。
2. **创建本轮对话**：`state.pending_turn = Turn(...)`。
3. **消息处理**：按消息类型分流
   - `TEXT` → `TurnPlanner` 意图识别 → `TurnPlan` → `TurnPlanValidator` 结构化命令校验 → `TurnPlanValidationResult(valid, reason)` → 校验通过则按轨道分发（`TaskHandler` / `KnowledgeHandler` / `ChitchatHandler`）；不通过则交 `ClarifyResponder` 澄清。
   - `OBJECT` → 写入 `state.focused_object`；若该对象可用于填槽则生成填槽命令交给任务轨道，否则进入澄清轨道。
4. **回填本轮对话**：把产生的机器回复写入 `state.pending_turn`。
5. **提交本轮对话**到当前会话。
6. **构造并返回** `ProcessResult`。

### 6. 意图识别 · TurnPlanner 输出结果的结构化约束

![TurnPlanner 输出结果的结构化约束](docs/images/06-turn-planner-output.png)

`TurnPlanner` 通过 LLM 对用户自然语言做三项判断：**① 进入哪个轨道？② 在该轨道做什么操作？③ 若为任务轨道，匹配哪个任务（流程）？**

- **任务轨道**：输出结构化命令，交给 `TaskHandler` 执行具体业务。

  ```json
  { "task": { "commands": [ { "command": "start_flow", "flow": "refund_request" } ] },
    "knowledge": null, "chitchat": null }
  ```

  命令种类（对应 `TaskHandler` 的处理）：

  | 命令 | 结构 | 含义 |
  | --- | --- | --- |
  | 启动任务 | `command="start_flow" flow="<flow_id>"` | 启动一个任务流程 |
  | 填槽命令 | `command="set_slots" slots={slot_name: slot_value}` | 为任务上下文写入槽位 |
  | 取消任务 | `command="cancel_flow"` | 取消当前任务 |
  | 恢复任务 | `command="resume_flow" flow="<flow_id>"` | 恢复被挂起的任务 |

  任务流程来自 YAML 定义（如 `query_order_status`、`refund_request`）。

- **知识轨道**：输出知识意图，交给 `KnowledgeHandler` 按意图检索回答。

  ```json
  { "task": null, "knowledge": { "intents": ["product_info", "refund_policy"] }, "chitchat": null }
  ```

  不同意图对应不同检索来源与后端：商品信息查询（`product_info`）→ 查询商品详情 → 电商业务后端；订单信息查询（`order_info`）→ 查询订单详情；商品操作咨询（`use_helper`）→ 查询使用手册 → RAG 系统；退货政策查询（`refund_policy`）→ 查询平台政策 → 平台政策 RAG 系统；保价政策查询（`price_protected_policy`）。

- **闲聊轨道**：输出 `chitchat`，交给 `ChitchatHandler`。

  ```json
  { "task": null, "knowledge": null, "chitchat": {} }
  ```

### 7. 意图识别 · TurnPlanner 生成结构化命令的实现流程

![TurnPlanner 生成结构化命令的实现流程](docs/images/07-turn-planner-pipeline.png)

输入 `state`、`flows`、`knowledge_intents`，三步产出结构化命令：

1. **渲染提示词**：把当前上下文注入模板，包括 `{{ available_flows_json }}`（任务轨道所有 flow 信息）、`{{ knowledge_intents_json }}`（知识轨道所有知识意图）、`{{ active_task_json }}`、`{{ interrupted_tasks_json }}`、`{{ focused_object_json }}`、`{{ current_conversation }}`、`{{ user_message }}`。
2. **调用 LLM**：让模型按「结构化命令：JSON」的约定输出 JSON。
3. **解析 JSON 结果**：反序列化为 `TurnPlan` 对象。

### 8. 意图识别 · TurnPlan 数据模型

![TurnPlan 数据模型](docs/images/08-turn-plan-model.png)

`TurnPlan` 用来存储意图识别后生成的结构化命令，通过 `from_dict` 从 JSON 还原：

- `TurnPlan`：`task: TaskTurnPlan|None`、`knowledge: KnowledgeTurnPlan|None`、`chitchat: ChitchatTurnPlan|None`。
- `TaskTurnPlan`：`commands: list[Command]`；`KnowledgeTurnPlan`：`intents: list[str]`；`ChitchatTurnPlan`：空。
- `Command`（基类，`command: str`）的四个子类：
  - `StartFlowCommand`：`flow: str`
  - `SetSlotsCommand`：`slots: dict`
  - `CancelFlowCommand`：无附加字段
  - `ResumeFlowCommand`：`flow: str`

### 9. 任务轨道 · TaskHandler 实现思路

![TaskHandler 实现思路](docs/images/09-task-handler.png)

`DialogueEngine` 把 `turn_plan.task` 的命令清单与 `state` 交给 `TaskHandler(flowslist)`，内部两步协作：

**① `CommandProcessor`：按命令修改 `state`**

| 命令 | 行为 |
| --- | --- |
| `start_flow` | 用命令中的 `flow_id` 构造 `TaskContext` 并设为 `active_task`；若当前已有正在执行的任务，则先把它挂起到 `paused_tasks` |
| `set_slots` | 把命令中的 `slots` 写入当前任务上下文的槽位 |
| `cancel_flow` | 清空当前任务上下文（被取消的任务直接丢弃） |
| `resume_flow` | 按 `flow_id` 从 `paused_tasks` 中取出任务并设为 `active_task` |

**② `FlowExecutor`（双层循环）：按 `state` 推进并执行流程**

- **外层循环**：反复调用内层循环推进流程，若返回的 `ActionCall.action_name` 为 `action_listen` 则结束；否则执行该 Action，并把结果消息收集起来。
- **内层循环**：判断当前任务上下文类型（用户任务 / 系统任务），取出对应 `flow` / `step`；按步骤类型推进（`start` 直接落到下一步、`collect` 缺槽则转系统收集流程、`action` 返回 `ActionCall`、`end` 结束任务），直到需要执行某个动作时把 `ActionCall` 抛出给外层。

`ActionCall` 交给 `ActionRunner`：按 `action_name` 从注册表取出 Action 实例并执行，得到 `ActionResult`（含 `messages` 与 `slot_updates`）。

### 10. 任务轨道 · Flow 数据模型

![Flow 数据模型](docs/images/10-flow-model.png)

- `FlowsList`：`slots: dict[str, FlowSlot]`、`flows: list[Flow]`。
- `Flow`：`id` / `name` / `description` / `steps: list[FlowStep]` / `slots: list[FlowSlot]`。
- `FlowSlot`：`name` / `type` / `label` / `description`。
- `FlowStep`：`id` / `type: FlowStepType` / `next: list[FlowStepLink]`；`FlowStepType` 为 `START / COLLECT / ACTION / END`，分别对应：
  - `StartFlowStep`
  - `CollectFlowStep`：`slot_name` / `response: ResponseDefinition` / `validation: SlotValidation|None`
  - `ActionFlowStep`：`action` / `args: str|dict[str, any]`
  - `EndFlowStep`
- `FlowStepLink`（`target: str`）的三种形态：`ConditionalLink`（`condition: str`）、`FallbackLink`、`StaticLink`。
- `SlotValidation`：`condition` / `failure_response: ResponseDefinition|None`；`ResponseDefinition`：`mode` / `text` / `prompt`。

> 原型中规划的槽位包括 `order_number`、`order_status`、`order_summary`、`tracking_number`、`logistics_company`、`logistics_status`、`refund_reason` 等；规划的流程包括 `order_status_query`、`refund_request`、`similar_product_recommendation`、`human_handoff`。

### 11. 知识轨道 · KnowledgeHandler

![KnowledgeHandler 轨道](docs/images/11-knowledge-handler.png)

`DialogueEngine` 把知识意图清单（如 `["refund_policy", "price_protected_policy"]`）交给 `KnowledgeHandler`，三步检索并回答：

1. 按 `intent_id` 查出该意图对应的 `provider_ids`。
2. 按 `provider_id` 从 `KnowledgeProviderRegistry` 取到对应的 Provider 实例。
3. 调用 Provider 的 `retrieve()` 得到 `List[KnowledgeChunk]`，再交 `KnowledgeResponder`（调用 LLM）组织成自然语言，产出本轮 `turns`（`user_message` + `list[BotMessage]`）。

`KnowledgeIntent`：`id` / `description` / `provider_ids` / `requires_object`；全部意图集中在 `KNOWLEDGE_INTENTS`。原型中的意图示例：`product_info`（查询商品信息，`requires_object="product"`）、`order_info`（查询订单信息，`requires_object="order"`）、`price_protected_policy`（查询保价政策）、`refund_policy`（查询退款政策）、`product_use_method`（查询商品使用手册）。

Provider 约定：每个 Provider 有唯一的 `provider_id`，且都必须实现 `retrieve()` 完成具体查询。

| Provider | `provider_id` | 查询对象 | 对接系统 |
| --- | --- | --- | --- |
| `ProductApiProvider` | `api.product` | 按商品 ID 查商品信息 | 电商业务后端 |
| `OrderApiProvider` | `api.order` | 按订单 ID 查订单信息 | 电商业务后端 |
| `FAQProvider` | `faq.default` | 查 FAQ | FAQ 系统 |
| `RAGProvider` | `rag.default` | 查知识库 | RAG 系统 |

> 注：原型中的意图清单为设计期版本，当前代码落地的意图见 `banban/knowledge/intents.py`。

## 技术栈

| 方向 | 选型 |
| --- | --- |
| 语言 / 包管理 | Python >= 3.11、[uv](https://docs.astral.sh/uv/) |
| Web 框架 | FastAPI（含 WebSocket，依赖 `websockets`） |
| 大模型接入 | LangChain（`init_chat_model` / `langchain-openai`，OpenAI 兼容接口） |
| 数据访问 | SQLAlchemy 2.x（异步）+ aiomysql |
| 异步 HTTP | httpx |
| 配置管理 | pydantic-settings（`.env` 驱动） |
| Prompt 模板 | Jinja2 |
| 流程配置 | YAML |

## 目录结构

```text
.
├── main.py                       # 服务入口（uvicorn 启动 FastAPI app）
├── pyproject.toml                # 项目元信息与依赖声明
├── uv.lock                       # 依赖版本锁定，请勿手改
├── .env.example                  # 配置模板
├── docs/images/                  # README 设计原型图
├── flow_config/                  # YAML 流程定义
│   ├── user_flows.yml            # 用户任务流程（订单状态、物流、退款、相似商品推荐…）
│   └── system_flows.yml          # 系统流程（信息收集、澄清、打断 / 恢复 / 取消…）
└── banban/
    ├── api/                      # API 层
    │   ├── app.py                # FastAPI 应用与 lifespan（初始化 DB / HTTP 客户端）
    │   ├── routers.py            # /api/chat、/api/chat/history、/ws/chat
    │   ├── deps.py               # 依赖装配（Service / Engine）
    │   └── schemas.py            # 请求 / 响应模型
    ├── service/                  # Service 层
    │   ├── dialogue_service.py   # 一次对话的编排（加载 → 处理 → 持久化）
    │   └── history_service.py    # 历史消息组装
    ├── engine/                   # Engine 层
    │   ├── dialogue_engine.py    # 顶层调度：会话准备、意图规划、轨道分发
    │   └── builder.py            # 组装引擎（加载流程、注册 Action、注入依赖）
    ├── plan/                     # 意图识别
    │   ├── models.py             # TurnPlan / TaskTurnPlan / KnowledgeTurnPlan
    │   ├── planner.py            # TurnPlanner（LLM 规划）
    │   └── validator.py          # TurnPlanValidator
    ├── task/                     # 任务轨道（规则引擎）
    │   ├── handler.py            # 任务处理入口
    │   ├── commands/             # 结构化命令模型与 CommandProcessor
    │   ├── flows/                # 流程模型、加载器、FlowExecutor
    │   └── action/               # 内置 / 自定义 Action、ActionRegistry、ActionRunner
    ├── knowledge/                # 知识轨道
    │   ├── handle.py             # KnowledgeHandler
    │   ├── intents.py            # 知识意图定义
    │   ├── providers.py          # 检索来源（业务 API / FAQ / RAG）
    │   ├── registry.py           # Provider 注册表
    │   └── responder.py          # 检索结果 → 自然语言回答
    ├── chitchat/                 # 闲聊轨道
    ├── clarify/                  # 澄清处理（含澄清原因）
    ├── domain/                   # 领域模型：DialogueState、任务 / 系统上下文、消息
    ├── repository/               # 持久化：对话状态读写（MySQL）
    ├── infrastructure/           # 基础设施
    │   ├── ai_clients.py         # LLM 客户端单例
    │   ├── database.py           # 异步引擎与会话工厂
    │   └── http_util.py          # 异步 HTTP 客户端单例
    ├── prompts/                  # Prompt 模板（Jinja2）与加载器
    ├── conf/config.py            # 全局配置单例 settings
    └── test/                     # 冒烟脚本（见「本地验证」）
```

## 快速开始

### 前置依赖

| 依赖 | 版本 / 地址 | 说明 |
| --- | --- | --- |
| Python | >= 3.11 | 由 uv 自动管理虚拟环境 |
| MySQL | 8.x | 建库 `customer_service`（`utf8mb4`）并建表 `dialogue_states`，见下方说明 |
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

启动后：

- 接口文档：<http://127.0.0.1:18082/docs>
- 对话接口：`POST http://127.0.0.1:18082/api/chat`
- WebSocket：`ws://127.0.0.1:18082/ws/chat`

> **需先建表**：服务**不会**自动建表。请先创建 `customer_service` 库与 `dialogue_states` 表：

```sql
CREATE DATABASE IF NOT EXISTS `customer_service`
  DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_unicode_ci;

USE `customer_service`;

CREATE TABLE IF NOT EXISTS `dialogue_states` (
  `sender_id`  VARCHAR(255) NOT NULL COMMENT '用户唯一标识',
  `state_json` TEXT         NOT NULL COMMENT '完整对话状态 JSON',
  PRIMARY KEY (`sender_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

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
uv run python -m banban.test.test_settings      # 1. 配置能否加载
uv run python -m banban.test.test_ai_clients    # 2. LLM 能否调通（需有效 API Key）
uv run python -m banban.test.test_database      # 3. MySQL 能否连通（需先启动数据库）
uv run python -m banban.test.test_http_util     # 4. 业务后端能否调通（需先启动业务后端）
uv run python -m banban.test.test_flow_load     # 5. YAML 流程能否正确加载
uv run python -m banban.test.test_turn_play     # 6. 意图规划能否跑通
uv run python -m banban.test.test_action_runner # 7. Action 注册与执行
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
