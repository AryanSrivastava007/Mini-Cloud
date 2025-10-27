import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from db import get_session
from models import Node, Task, Instance

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/{node_id}/heartbeat")
def heartbeat(node_id: str, name: str, session: Session = Depends(get_session)):
    node = session.get(Node, node_id)
    if not node:
        node = Node(id=node_id, name=name, last_heartbeat_at=datetime.now(timezone.utc))
        session.add(node)
    else:
        node.last_heartbeat_at = datetime.now(timezone.utc)
    session.commit()
    return {"ok": True}

@router.post("/{node_id}/next-task")
def next_task(node_id: str, session: Session = Depends(get_session)):
    # Claim one READY task
    task = session.exec(select(Task).where(Task.status=="READY").order_by(Task.id)).first()
    if not task:
        return "", 204
    task.status = "TAKEN"
    task.node_id = node_id
    session.add(task)
    session.commit()
    return {"id": task.id, "type": task.type, "payload": json.loads(task.payload_json)}

@router.post("/tasks/{task_id}/complete")
def task_complete(task_id: int, container_id: str, mapped_port: int | None,
                  status: str, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "task not found")
    payload = json.loads(task.payload_json)
    inst = session.get(Instance, payload["instance_id"])
    if not inst:
        raise HTTPException(404, "instance not found")

    inst.status = status
    if status == "RUNNING":
        inst.node_id = task.node_id
        inst.container_id = container_id
        inst.mapped_port = mapped_port
    task.status = "DONE"
    session.add(inst); session.add(task); session.commit()
    return {"ok": True}

@router.post("/tasks/{task_id}/fail")
def task_fail(task_id: int, error: str, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "task not found")
    payload = json.loads(task.payload_json)
    inst = session.get(Instance, payload["instance_id"])
    if inst:
        inst.status = "FAILED"
        session.add(inst)
    task.status = "FAILED"
    session.add(task); session.commit()
    return {"ok": True}