from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Node(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    last_heartbeat_at: datetime | None = None
    capacity_cpu: float = 2.0
    capacity_mem_mb: int = 2048

class Instance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    image: str  # e.g., "nginx:alpine"
    cpu: float = 0.5
    mem_mb: int = 256
    status: str = "PENDING"  # PENDING | RUNNING | FAILED | STOPPED
    node_id: Optional[str] = None
    container_id: Optional[str] = None
    mapped_port: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str  # "CREATE_INSTANCE"
    payload_json: str
    status: str = "READY"  # READY | TAKEN | DONE | FAILED
    node_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)