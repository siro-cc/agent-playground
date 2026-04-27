CASES = [
    {"question": "集群整体状态如何？", "expected_intent": "cluster_status", "expected_tool": "get_cluster_status"},
    {"question": "cluster-a 健康吗？", "expected_intent": "cluster_status", "expected_tool": "get_cluster_status"},
    {"question": "payment-service 有告警吗？", "expected_intent": "alerts", "expected_tool": "query_alerts"},
    {"question": "user-service 最近发过版吗？", "expected_intent": "recent_changes", "expected_tool": "get_recent_changes"},
    {"question": "user-service 当前状态如何？", "expected_intent": "service_status", "expected_tool": "query_service_status"},
    {"question": "Pod 一直 CrashLoopBackOff，先怎么排查？", "expected_intent": "runbook", "expected_tool": "search_runbook"},
    {"question": "CPU 高怎么定位？", "expected_intent": "runbook", "expected_tool": "search_runbook"},
    {"question": "这个系统不太对劲", "expected_intent": "unknown", "expected_tool": None},
    {"question": "帮我看看哪里有问题", "expected_intent": "unknown", "expected_tool": None},
    {"question": "服务启动失败，一般先看什么？", "expected_intent": "runbook", "expected_tool": "search_runbook"},
]