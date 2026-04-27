# agent-playground

Minimal FastAPI project managed with `uv`.

## 项目目标
## 当前能力
## 技术栈
## 目录结构
## 启动方式
## API 示例
## 支持的工具
## 手工测试 Case
## 当前限制
## 下周计划


## Week 3 Progress

- 新增最小状态结构 AgentState
- 新增流程版接口 /flow
- 新增意图识别逻辑
- 新增参数提取函数：
  - extract_cluster_name
  - extract_service_name
- 减少工具参数硬编码默认值
- Week 3 flow 评测准确率提升

## Week 4 Progress

- 新增节点化流程引擎 flow_engine.py
- 新增节点文件 flow_nodes.py
- 状态对象新增 current_stage / requires_approval / approved
- history 从字符串列表升级为结构化阶段记录
- 新增 approval_gate_node 占位
- 新增 /flow-v3 接口
- 新增阻断型流程测试

## Configuration

The app loads configuration from `.env`.

Example:

```bash
cp .env.example .env
```

## Run

```bash
uv sync
uv run uvicorn app.main:app --reload
```

Or use the startup script:

```bash
./start.sh
```

Optional overrides:

```bash
HOST=0.0.0.0 PORT=9000 RELOAD=false ./start.sh
```

## Endpoints

- `GET /health`: liveness probe
- `GET /ready`: readiness probe
- `POST /chat`: returns the fixed chat status message
