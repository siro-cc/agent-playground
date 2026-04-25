from app.agent import run_agent

CASES = [
    {"question": "test-cluster 现在状态怎么样？", "expected_tool": "get_cluster_status"},
    {"question": "cluster-a 健康吗？", "expected_tool": "get_cluster_status"},
    {"question": "user-service 当前状态如何？", "expected_tool": "query_service_status"},
    {"question": "payment-service 现在有告警吗？", "expected_tool": "query_alerts"},
    {"question": "user-service 最近有变更吗？", "expected_tool": "get_recent_changes"},
    {"question": "Pod 一直 CrashLoopBackOff，先怎么排查？", "expected_tool": "search_runbook"},
    {"question": "服务启动失败，一般先看什么？", "expected_tool": "search_runbook"},
    {"question": "CPU 高怎么定位？", "expected_tool": "search_runbook"},
]

def main() -> None:
    passed = 0

    for idx, case in enumerate(CASES, start=1):
        resp = run_agent(case["question"])
        ok = resp.tool_used == case["expected_tool"]
        if ok:
            passed += 1

        print("=" * 60)
        print(f"Case {idx}")
        print("Question      :", case["question"])
        print("Expected Tool :", case["expected_tool"])
        print("Actual Tool   :", resp.tool_used)
        print("Pass          :", ok)
        print("Error         :", resp.error)

    print("=" * 60)
    print(f"Score: {passed}/{len(CASES)}")


if __name__ == "__main__":
    main()