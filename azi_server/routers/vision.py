from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..brain import vision

router = APIRouter(
    prefix="/api/vision",
    tags=["vision"]
)

class EvaluateReq(BaseModel):
    image: str # Base64
    prompt: str = "Bunu analiz et"

@router.post("/scan")
async def analyze_image(req: EvaluateReq):
    """
    Kameradan gelen görüntüyü yapay zekaya yorumlatır.
    """
    result = vision.vision_service.analyze_frame(req.image, req.prompt)
    if not result["success"]:
        # Frontend catch bloğuna detaylı hata gönder
        error_msg = result.get("analysis", result.get("error", "Bilinmeyen Hata"))
        raise HTTPException(status_code=500, detail=error_msg)
    
    return result
