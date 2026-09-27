import logging
from fastapi import APIRouter, Depends

from app.schemas.translate import TranslateRequest, TranslateResponse
from app.services.sarvam import get_sarvam_service, SarvamTranslationService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/translate", response_model=TranslateResponse)
async def translate_text(
    request: TranslateRequest,
    sarvam_svc: SarvamTranslationService = Depends(get_sarvam_service)
):
    """
    Translates Indian-language procurement requirements into English using Sarvam AI.
    
    Behavior:
    - If input is already in English, Sarvam is NOT called (bypassed).
    - If input contains Indian-language script, calls Sarvam's sarvam-translate:v1.
    - Errors are handled gracefully and return a friendly error message with fallback text.
    - API keys remain strictly backend-only.
    """
    return await sarvam_svc.translate_requirement(
        text=request.text,
        source_language_code=request.source_language_code
    )
