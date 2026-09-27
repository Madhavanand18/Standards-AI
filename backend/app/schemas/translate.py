from pydantic import BaseModel, Field

class TranslateRequest(BaseModel):
    """Request model for Sarvam AI Indian-language translation."""
    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Procurement specification or requirement text to translate"
    )
    source_language_code: str = Field(
        default="auto",
        description="Source language BCP-47 code or 'auto' for automatic detection"
    )

class TranslateResponse(BaseModel):
    """Response model for translation result."""
    success: bool = True
    original_text: str
    translated_text: str
    source_language_code: str | None = None
    is_translated: bool = False
    provider: str = "sarvam"
    model: str = "sarvam-translate:v1"
    message: str | None = None
    error: str | None = None
