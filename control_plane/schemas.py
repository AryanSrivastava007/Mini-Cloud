from typing import Optional
from pydantic import BaseModel

class InstanceCreate(BaseModel):
    name: str
    image: str
    cpu: float = 0.5
    mem_mb: int = 256
    port_in: int = 80
    port_out: Optional[int] = None

class InstanceOut(BaseModel):
    id: int
    name: str
    image: str
    status: str
    node_id: Optional[str] = None
    mapped_port: Optional[int] = None