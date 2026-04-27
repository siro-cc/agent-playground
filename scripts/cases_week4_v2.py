CASES = [
    {
        "question": "cluster-a 健康吗？",
        "approved": False,
        "expected_stage_end": "build_response",
        "expected_requires_approval": False,
    },
    {
        "question": "payment-service 有告警吗？",
        "approved": False,
        "expected_stage_end": "build_response",
        "expected_requires_approval": False,
    },
    {
        "question": "user-service 最近发过版吗？",
        "approved": False,
        "expected_stage_end": "approval_gate",
        "expected_requires_approval": True,
    },
    {
        "question": "user-service 最近发过版吗？",
        "approved": True,
        "expected_stage_end": "build_response",
        "expected_requires_approval": True,
    },
    {
        "question": "帮我看看哪里有问题",
        "approved": False,
        "expected_stage_end": "build_response",
        "expected_requires_approval": False,
    },
]