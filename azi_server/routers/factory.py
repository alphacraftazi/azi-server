from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from ..brain.factory import factory_service
import os

router = APIRouter(prefix="/api/factory", tags=["factory"])

class PackageReq(BaseModel):
    license_key: Optional[str] = None
    product_type: Optional[str] = None 
    business_name: Optional[str] = "Business"
    custom_requirements: Optional[str] = None

@router.post("/package/{license_key}")
async def package_product(license_key: str, product_type: str = "stock", req: PackageReq = None):
    # Eğer body gelmezse query params kullanilir, ama hibrit destekleyelim
    custom = req.custom_requirements if req else None
    biz_name = req.business_name if req else "Business"
    
    # Bugfix: Body varsa type oradan alınmalı (Frontend query göndermiyor)
    if req and req.product_type:
        product_type = req.product_type
        
    print(f"DEBUG: Packaging Request - Final Type: {product_type} (Body: {req.dict() if req else 'None'})")
    
    # Normalize
    product_type = product_type.lower().strip()
    
    result = factory_service.package_client(license_key, product_type, custom, biz_name)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=result["error"])

@router.get("/download/{filename}")
async def download_installer(filename: str):
    from fastapi.responses import FileResponse
    
    file_path = os.path.join(factory_service.installers_path, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    else:
        raise HTTPException(status_code=404, detail="Installer not found")
