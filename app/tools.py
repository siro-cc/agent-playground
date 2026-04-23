from typing import Any, Dict, List


def get_cluster_status(cluster_name: str) -> Dict[str, Any]:
    """
    假数据版集群状态查询工具
    后续可以替换为真实的kubernetes API 查询
    """
    cluster_name = (cluster_name or "").strip()
    if not cluster_name:
        raise ValueError("cluster_name 不能为空")

    mock_clusters = {
        "test-cluster": {
            "cluster_name": "test-cluster",
            "status": "healthy",
            "node_count": 3,
            "ready_node_count": 3,
            "namespace_count": 12,
            "warning": None,
        },
        "cluster-a": {
            "cluster_name": "cluster-a",
            "status": "warning",
            "node_count": 5,
            "ready_node_count": 4,
            "namespace_count": 20,
            "warning": "1 个节点 NotReady，请检查节点网络或 kubelet 状态",
        },
        "cluster-b": {
            "cluster_name": "cluster-b",
            "status": "critical",
            "node_count": 4,
            "ready_node_count": 2,
            "namespace_count": 18,
            "warning": "控制面或节点异常，建议立即排查 apiserver / etcd / 节点健康状态",
        },
    }

    default_result = {
        "cluster_name": cluster_name,
        "status": "unknown",
        "node_count": 0,
        "ready_node_count": 0,
        "namespace_count": 0,
        "warning": f"未找到集群 {cluster_name} 的状态信息，请确认集群名称是否正确",
    }

    return mock_clusters.get(cluster_name, default_result)


def search_runbook(keyword: str) -> Dict[str, Any]:
    """
    假数据版排障手册检索工具。
    后续可以替换为向量检索/全文检索。
    """
    keyword = (keyword or "").strip()

    if not keyword:
        raise ValueError("keyword 不能为空")

    runbook_library: List[Dict[str, Any]] = [
        {
            "match_keywords": [
                "CrashLoopBackOff",
                "crashloopbackoff",
                "pod重启",
                "容器反复重启",
            ],
            "title": "Pod CrashLoopBackOff 排查手册",
            "summary": "优先检查容器启动命令、环境变量、依赖服务连通性、存活探针与启动探针配置，以及最近一次变更。",
            "steps": [
                "查看 Pod 事件与容器退出码",
                "检查启动命令和环境变量是否正确",
                "检查依赖的数据库、缓存、配置中心是否可达",
                "检查 liveness/readiness/startup probe 配置",
                "核对最近镜像、配置、发布变更",
            ],
        },
        {
            "match_keywords": ["启动失败", "服务启动失败", "应用启动失败"],
            "title": "服务启动失败通用排查手册",
            "summary": "先看应用日志、启动参数、配置文件、端口占用和外部依赖连通性，再结合最近变更判断。",
            "steps": [
                "查看应用启动日志和异常堆栈",
                "检查配置文件、环境变量、密钥是否缺失",
                "检查端口占用和权限问题",
                "检查数据库、Redis、MQ 等依赖是否可连通",
                "核对最近代码、镜像、配置发布记录",
            ],
        },
        {
            "match_keywords": ["cpu高", "CPU高", "负载高", "资源高"],
            "title": "CPU 负载过高排查手册",
            "summary": "先确认是单 Pod 还是整体服务异常，再结合监控、线程栈和最近流量变化定位热点。",
            "steps": [
                "确认 CPU 高的范围：单 Pod、单节点还是整个服务",
                "查看监控曲线与流量变化",
                "分析线程栈或 pprof",
                "检查是否存在死循环、频繁重试、异常流量",
                "核对最近上线和配置变更",
            ],
        },
    ]
    keyword_lower = keyword.lower()
    matched_docs = []
    for doc in runbook_library:
        matched = any(
            k.lower() in keyword_lower or keyword_lower in k.lower()
            for k in doc["match_keywords"]
        )
        if matched:
            matched_docs.append(
                {
                    "title": doc["title"],
                    "summary": doc["summary"],
                    "steps": doc["steps"],
                }
            )
    return {
        "keyword": keyword,
        "matched": len(matched_docs) > 0,
        "documents": matched_docs,
        "count": len(matched_docs),
    }
