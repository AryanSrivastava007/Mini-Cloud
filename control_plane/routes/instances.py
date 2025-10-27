import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from db import get_session
from models import Instance, Task
from schemas import InstanceCreate, InstanceOut

router = APIRouter(prefix="/instances", tags=["instances"])

@router.get("/", response_model=list[InstanceOut])
def list_instances(session: Session = Depends(get_session)):
    rows = session.exec(select(Instance)).all()
    return [InstanceOut(id=r.id, name=r.name, image=r.image,
                        status=r.status, node_id=r.node_id, mapped_port=r.mapped_port) for r in rows]

@router.post("/", response_model=InstanceOut, status_code=201)
def create_instance(body: InstanceCreate, session: Session = Depends(get_session)):
    inst = Instance(name=body.name, image=body.image, cpu=body.cpu, mem_mb=body.mem_mb, status="PENDING")
    session.add(inst); session.commit(); session.refresh(inst)

    # Simple scheduling: leave node_id empty; any agent can pick it up
    payload = body.model_dump()
    payload["instance_id"] = inst.id
    session.add(Task(type="CREATE_INSTANCE", payload_json=json.dumps(payload), status="READY"))
    session.commit()

    return InstanceOut(id=inst.id, name=inst.name, image=inst.image, status=inst.status,
                       node_id=inst.node_id, mapped_port=inst.mapped_port)