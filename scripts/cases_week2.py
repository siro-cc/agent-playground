CASES = [
    # A. 集群类
    {"question": "test-cluster 现在状态怎么样？", "expected_tool": "get_cluster_status", "category": "cluster"},
    {"question": "cluster-a 健康吗？", "expected_tool": "get_cluster_status", "category": "cluster"},
    {"question": "cluster-b 节点正常吗？", "expected_tool": "get_cluster_status", "category": "cluster"},
    {"question": "这个集群是不是有问题？", "expected_tool": "get_cluster_status", "category": "cluster"},
    {"question": "集群整体状态如何？", "expected_tool": "get_cluster_status", "category": "cluster"},

    # B. 服务状态类
    {"question": "user-service 当前状态如何？", "expected_tool": "query_service_status", "category": "service_status"},
    {"question": "payment-service 运行正常吗？", "expected_tool": "query_service_status", "category": "service_status"},
    {"question": "user-service 的副本是不是不够？", "expected_tool": "query_service_status", "category": "service_status"},
    {"question": "user-service 现在是不是降级了？", "expected_tool": "query_service_status", "category": "service_status"},
    {"question": "payment-service 当前副本情况怎么样？", "expected_tool": "query_service_status", "category": "service_status"},

    # C. 告警/变更类
    {"question": "payment-service 现在有告警吗？", "expected_tool": "query_alerts", "category": "alerts"},
    {"question": "user-service 最近有变更吗？", "expected_tool": "get_recent_changes", "category": "changes"},
    {"question": "user-service 最近发过版吗？", "expected_tool": "get_recent_changes", "category": "changes"},
    {"question": "payment-service 最近动过配置吗？", "expected_tool": "get_recent_changes", "category": "changes"},
    {"question": "user-service 当前是否有异常告警？", "expected_tool": "query_alerts", "category": "alerts"},

    # D. 排障手册类
    {"question": "Pod 一直 CrashLoopBackOff，先怎么排查？", "expected_tool": "search_runbook", "category": "runbook"},
    {"question": "服务启动失败，一般先看什么？", "expected_tool": "search_runbook", "category": "runbook"},
    {"question": "CPU 高怎么定位？", "expected_tool": "search_runbook", "category": "runbook"},
    {"question": "容器反复重启怎么排查？", "expected_tool": "search_runbook", "category": "runbook"},
    {"question": "应用启动不起来怎么分析？", "expected_tool": "search_runbook", "category": "runbook"},
]