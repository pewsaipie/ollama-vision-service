from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl, conlist
from ..vision.inference import extract_text

router = APIRouter(prefix="/v1", tags=["vision"])

class VisionRequest(BaseModel):
    model: str = "llava"
    prompt: str = "Describe the image."
    images: conlist(HttpUrl, min_items=1, max_items=5)

class VisionResponse(BaseModel):
    text: str

@router.post("/infer", response_model=VisionResponse, status_code=status.HTTP_200_OK)
async def infer(req: VisionRequest):
    """
    Submit an image (or list of images) and a prompt to Ollama's vision model.
    Returns the extracted text.
    """
    try:
        # `extract_text` currently expects a single image path; we pass the first URL.
        # In a real implementation you could download the image and handle multiple.
        result_text = await extract_text(req.images[0], model=req.model)
        return VisionResponse(text=result_text)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc)
        )