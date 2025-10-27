import os, time, requests, random
import docker

CONTROL = os.getenv("CONTROL_PLANE_URL", "http://localhost:8000")
NODE_ID = os.getenv("NODE_ID", "node-1")
NODE_NAME = f"Agent {NODE_ID}"
POLL_SEC = 1.5

client = docker.from_env()

def heartbeat():
    try:
        requests.post(f"{CONTROL}/agents/{NODE_ID}/heartbeat", params={"name": NODE_NAME}, timeout=5)
    except requests.RequestException:
        pass

def take_task():
    try:
        r = requests.post(f"{CONTROL}/agents/{NODE_ID}/next-task", timeout=5)
        if r.status_code == 204:
            return None
        return r.json()
    except requests.RequestException:
        return None

def complete(task_id, container_id, mapped_port, status="RUNNING"):
    try:
        requests.post(f"{CONTROL}/agents/tasks/{task_id}/complete",
                      params={"container_id": container_id, "mapped_port": mapped_port, "status": status}, timeout=5)
    except requests.RequestException:
        pass

def fail(task_id, error):
    try:
        requests.post(f"{CONTROL}/agents/tasks/{task_id}/fail", params={"error": error}, timeout=5)
    except requests.RequestException:
        pass

def run_container(image: str, port_in: int, port_out: int | None, cpu: float, mem_mb: int):
    # random host port if not given
    if port_out is None:
        port_out = random.randint(20000, 40000)
    nano_cpus = int(cpu * 1e9)  # 1.0 = 1 CPU
    container = client.containers.run(
        image, detach=True,
        nano_cpus=nano_cpus,
        mem_limit=f"{mem_mb}m",
        ports={f"{port_in}/tcp": port_out},
        name=f"minicloud-{random.randint(1000,9999)}",
    )
    return container, port_out

if __name__ == "__main__":
    while True:
        heartbeat()
        task = take_task()
        if not task:
            time.sleep(POLL_SEC); continue

        try:
            if task["type"] == "CREATE_INSTANCE":
                p = task["payload"]
                c, mapped = run_container(
                    image=p["image"],
                    port_in=p.get("port_in", 80),
                    port_out=p.get("port_out"),
                    cpu=p.get("cpu", 0.5),
                    mem_mb=p.get("mem_mb", 256),
                )
                complete(task["id"], c.id, mapped, status="RUNNING")
            else:
                fail(task["id"], f"unknown task {task['type']}")
        except Exception as e:
            try:
                fail(task["id"], str(e))
            except Exception:
                pass
            time.sleep(1)