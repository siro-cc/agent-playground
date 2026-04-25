# Tools Design

## 1. get_cluster_status
### 用途
查询指定集群的健康状态、节点数量和告警信息。

### 输入参数
- cluster_name: string

### 输出字段
- cluster_name
- status
- node_count
- ready_node_count
- namespace_count
- warning

### 失败返回
- cluster_name 不能为空
- 未找到指定集群

---

## 2. search_runbook
### 用途
根据故障关键词检索排障手册。

### 输入参数
- keyword: string

### 输出字段
- keyword
- matched
- documents
- count

### 失败返回
- keyword 不能为空

---

## 3. query_alerts
### 用途
查询某服务最近的告警摘要。

### 输入参数
- service_name: string
- time_range: string

### 输出字段
- service_name
- alert_count
- top_alerts
- severity_summary

### 失败返回
- service_name 不能为空

---

## 4. get_recent_changes
### 用途
查询最近变更记录，用于排查“是不是刚发版导致”。

### 输入参数
- service_name: string

### 输出字段
- service_name
- changes
- latest_change_time

### 失败返回
- service_name 不能为空

---

## 5. query_service_status
### 用途
查询某服务实例、Pod 或进程状态。

### 输入参数
- service_name: string

### 输出字段
- service_name
- status
- instance_count
- abnormal_instances

### 失败返回
- service_name 不能为空