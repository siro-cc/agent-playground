
from app.tools import get_cluster_status, search_runbook


print("== get_cluster_status ==")
print(get_cluster_status("test-cluster"))
print(get_cluster_status("cluster-a"))

print("\n== search_runbook ==")
print(search_runbook("Pod 一直 CrashLoopBackOff，怎么排查？"))
print(search_runbook("服务启动失败，一般先看什么？"))