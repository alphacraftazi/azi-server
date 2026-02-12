from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import time
from .. import models, database
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])

# In-Memory Command Queue for Active Sessions
# { "LICENSE_KEY": [ { "action": "popup", "args": {...} } ] }
command_queue: Dict[str, list] = {}

class PingReq(BaseModel):
    license_key: str
    status: str
    app: str
    timestamp: float
    data_hash: Optional[str] = None

class CommandReq(BaseModel):
    license_key: str
    command: str
    args: dict

from ..brain import core_products

@router.post("/ping")
async def telemetry_ping(req: PingReq, db: Session = Depends(database.get_db)):
    """Receives heartbeat from client products."""
    # 1. Update DB Status
    core_products.product_service.update_status(db, req.license_key, req.status)
    
    # Debug log (Optional, can be removed later)
    # print(f"TELEMETRY PING: [{req.app}] {req.license_key} is {req.status}")
    
    return {"status": "ack"}

@router.get("/command")
async def get_command(license: str):
    """Clients poll this to see if there are pending commands."""
    if license in command_queue and command_queue[license]:
        cmd = command_queue[license].pop(0)
        return cmd
    return {}

# Internal Endpoint for AZI Brain to push commands
@router.post("/send_command")
async def push_command(req: CommandReq):
    if req.license_key not in command_queue:
        command_queue[req.license_key] = []
    
    command_queue[req.license_key].append({
        "action": req.command,
        "args": req.args
    })
    return {"status": "queued", "queue_len": len(command_queue[req.license_key])}
