CASES = [
    {
        "question": "cluster-a 健康吗？",
        "expected_intent": "cluster_status",
        "expected_tool": "get_cluster_status",
        "expected_stage_end": "build_response",
    },
    {
        "question": "payment-service 有告警吗？",
        "expected_intent": "alerts",
        "expected_tool": "query_alerts",
        "expected_stage_end": "build_response",
    },
    {
        "question": "user-service 最近发过版吗？",
        "expected_intent": "recent_changes",
        "expected_tool": "get_recent_changes",
        "expected_stage_end": "build_response",
    },
    {
        "question": "user-service 当前状态如何？",
        "expected_intent": "service_status",
        "expected_tool": "query_service_status",
        "expected_stage_end": "build_response",
    },
    {
        "question": "CPU 高怎么定位？",
        "expected_intent": "runbook",
        "expected_tool": "search_runbook",
        "expected_stage_end": "build_response",
    },
    {
        "question": "帮我看看哪里有问题",
        "expected_intent": "unknown",
        "expected_tool": None,
        "expected_stage_end": "build_response",
    },
]