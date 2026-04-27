# Week 3 Findings

## 本轮主要问题

### 1. 集群命名模式未覆盖
- 问题示例：cluster-a 健康吗？
- 原因：classify_intent 未识别 cluster-* 模式
- 修复方式：增加 cluster 正则匹配

### 2. 变更类口语表达未覆盖
- 问题示例：user-service 最近发过版吗？
- 原因：未覆盖“发版/发过版”等表达
- 修复方式：增加 recent_changes 同义关键词

### 3. 参数提取仍存在硬编码默认值
- 现状：cluster/service 仍使用固定值兜底
- 风险：即使意图正确，也可能查错对象
- 修复方向：引入集群名/服务名提取函数