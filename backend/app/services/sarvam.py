"""
Sarvam AI Indian-Language Translation Service — Feature 2.

Provides backend-only translation of Indian-language procurement requirements
into English specifications using Sarvam AI's text translation API (model: sarvam-translate:v1).

Strict Constraints:
- English input is NOT sent to Sarvam (direct passthrough).
- Indian-language input is sent once per search.
- API key is loaded from settings / backend/.env and never exposed to frontend or in logs.
- Requests limited strictly to requirement text (max 2000 chars).
- API errors handled gracefully with user-friendly diagnostics.
"""

from __future__ import annotations

import logging
import re
from typing import Any
import httpx

from app.core.config import settings
from app.schemas.translate import TranslateResponse

logger = logging.getLogger("standards_ai.sarvam")

# Unicode ranges covering 22 official scheduled Indian language scripts:
# Devanagari (\u0900-\u097F), Bengali/Assamese (\u0980-\u09FF), Gurmukhi (\u0A00-\u0A7F),
# Gujarati (\u0A80-\u0AFF), Odia (\u0B00-\u0B7F), Tamil (\u0B80-\u0BFF),
# Telugu (\u0C00-\u0C7F), Kannada (\u0C80-\u0CFF), Malayalam (\u0D00-\u0D7F),
# Perso-Arabic / Urdu / Kashmiri / Sindhi (\u0600-\u06FF)
INDIC_SCRIPT_PATTERN = re.compile(r"[\u0900-\u0D7F\u0600-\u06FF]")

# Mapping of Indic script Unicode blocks to Sarvam-supported BCP-47 language codes
INDIC_SCRIPT_TO_LANG: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"[\u0C00-\u0C7F]"), "te-IN"),  # Telugu
    (re.compile(r"[\u0B80-\u0BFF]"), "ta-IN"),  # Tamil
    (re.compile(r"[\u0C80-\u0CFF]"), "kn-IN"),  # Kannada
    (re.compile(r"[\u0D00-\u0D7F]"), "ml-IN"),  # Malayalam
    (re.compile(r"[\u0A80-\u0AFF]"), "gu-IN"),  # Gujarati
    (re.compile(r"[\u0A00-\u0A7F]"), "pa-IN"),  # Punjabi (Gurmukhi)
    (re.compile(r"[\u0980-\u09FF]"), "bn-IN"),  # Bengali / Assamese
    (re.compile(r"[\u0B00-\u0B7F]"), "od-IN"),  # Odia
    (re.compile(r"[\u0600-\u06FF]"), "ur-IN"),  # Urdu (Perso-Arabic)
    (re.compile(r"[\u0900-\u097F]"), "hi-IN"),  # Hindi / Devanagari (Marathi, Sanskrit, etc.)
]

# Maximum characters allowed by sarvam-translate:v1 per request
SARVAM_MAX_CHARACTERS = 2000


def contains_indic_script(text: str) -> bool:
    """Returns True if the text contains any Indian-language script characters."""
    return bool(INDIC_SCRIPT_PATTERN.search(text))


def resolve_source_language_code(text: str, requested_code: str | None = None) -> str:
    """
    Resolves the source language code for Sarvam's sarvam-translate:v1.
    If requested_code is an explicit BCP-47 code other than 'auto', it is preserved.
    If requested_code is 'auto', None, or empty, automatically identifies the
    appropriate BCP-47 code from the input text script (e.g. te-IN, hi-IN, ta-IN).
    """
    if requested_code and requested_code.strip().lower() not in ("auto", ""):
        return requested_code.strip()

    for pattern, code in INDIC_SCRIPT_TO_LANG:
        if pattern.search(text):
            return code

    return "hi-IN"


def is_already_english(text: str) -> bool:
    """
    Determines if input text is standard English and should bypass Sarvam translation.
    Returns True if text has no Indic script characters.
    """
    cleaned = text.strip()
    if not cleaned:
        return True
    return not contains_indic_script(cleaned)


class SarvamTranslationService:
    """Service client for Sarvam AI Text Translation."""

    def __init__(self) -> None:
        self.api_url = settings.SARVAM_TRANSLATE_URL
        self.model = settings.SARVAM_TRANSLATE_MODEL
        self.timeout = settings.SARVAM_REQUEST_TIMEOUT_SECONDS

    @property
    def is_configured(self) -> bool:
        """Returns True if SARVAM_API_KEY is present in settings."""
        key = settings.SARVAM_API_KEY
        return bool(key and key.strip())

    async def translate_requirement(
        self,
        text: str,
        source_language_code: str = "auto"
    ) -> TranslateResponse:
        """
        Translates Indian-language requirement into English using Sarvam AI.

        Behavior:
        1. English input: Direct passthrough, does NOT call Sarvam.
        2. Indian-language input: Calls Sarvam's sarvam-translate:v1 model.
        3. Errors: Caught gracefully; returns fallback response with user-friendly error note.
        """
        raw_text = text.strip()
        if not raw_text:
            return TranslateResponse(
                success=True,
                original_text="",
                translated_text="",
                source_language_code=None,
                is_translated=False,
                message="Empty text provided."
            )

        # Rule 1 & 4: Do not translate already-English input
        if is_already_english(raw_text):
            logger.info("Text contains no Indic script characters. Bypassing Sarvam translation.")
            return TranslateResponse(
                success=True,
                original_text=raw_text,
                translated_text=raw_text,
                source_language_code="en-IN",
                is_translated=False,
                message="English input detected; translation bypassed."
            )

        # Check API key configuration
        if not self.is_configured:
            logger.warning("SARVAM_API_KEY is not configured in backend/.env. Translation cannot proceed.")
            return TranslateResponse(
                success=False,
                original_text=raw_text,
                translated_text=raw_text,
                source_language_code=None,
                is_translated=False,
                error="Sarvam AI API key is not configured in backend/.env."
            )

        # Limit request strictly to the user's requirement text (max 2000 chars)
        trimmed_input = raw_text[:SARVAM_MAX_CHARACTERS]

        # Resolve source language code:
        # sarvam-translate:v1 does not accept 'auto' (HTTP 400 'Invalid language code auto').
        # We automatically detect the BCP-47 Indian language code from the input script.
        resolved_source_lang = resolve_source_language_code(trimmed_input, source_language_code)

        payload: dict[str, Any] = {
            "input": trimmed_input,
            "source_language_code": resolved_source_lang,
            "target_language_code": "en-IN",
            "model": self.model
        }

        # Header for Sarvam authentication (Backend-only, never sent to frontend)
        headers = {
            "api-subscription-key": settings.SARVAM_API_KEY.strip(),
            "Content-Type": "application/json"
        }

        try:
            logger.info(
                f"Calling Sarvam AI translate ({self.model}) for Indian-language requirement "
                f"({len(trimmed_input)} chars, source: {resolved_source_lang})..."
            )
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                translated = data.get("translated_text", "").strip()
                detected_lang = data.get("source_language_code") or resolved_source_lang

                if translated:
                    logger.info(f"Sarvam translation successful (source: {detected_lang}).")
                    return TranslateResponse(
                        success=True,
                        original_text=raw_text,
                        translated_text=translated,
                        source_language_code=detected_lang,
                        is_translated=True,
                        message="Translated successfully via Sarvam AI."
                    )
                else:
                    logger.warning("Sarvam returned HTTP 200 but empty translated_text.")
                    return TranslateResponse(
                        success=True,
                        original_text=raw_text,
                        translated_text=raw_text,
                        source_language_code=detected_lang,
                        is_translated=False,
                        message="Empty translation returned; using original requirement."
                    )

            # Non-200 responses handled gracefully
            status_code = response.status_code
            error_detail = response.text
            logger.warning(f"Sarvam API returned HTTP {status_code}: {error_detail}")

            user_error_msg = f"Sarvam AI service returned HTTP {status_code}."
            try:
                err_json = response.json()
                if isinstance(err_json, dict) and "error" in err_json:
                    err_obj = err_json["error"]
                    if isinstance(err_obj, dict) and "message" in err_obj:
                        user_error_msg = f"Sarvam AI: {err_obj['message']}"
                    elif isinstance(err_obj, str):
                        user_error_msg = f"Sarvam AI: {err_obj}"
                elif isinstance(err_json, dict) and "detail" in err_json:
                    user_error_msg = f"Sarvam AI: {err_json['detail']}"
            except Exception:
                if status_code in (401, 403):
                    user_error_msg = "Sarvam AI authentication failed. Please check the API key."
                elif status_code == 429:
                    user_error_msg = "Sarvam AI rate limit exceeded. Please try again shortly."
                elif status_code >= 500:
                    user_error_msg = "Sarvam AI translation service is temporarily unavailable."

            return TranslateResponse(
                success=False,
                original_text=raw_text,
                translated_text=raw_text,
                source_language_code=None,
                is_translated=False,
                error=user_error_msg
            )

        except httpx.TimeoutException:
            logger.warning(f"Sarvam API request timed out after {self.timeout}s.")
            return TranslateResponse(
                success=False,
                original_text=raw_text,
                translated_text=raw_text,
                source_language_code=None,
                is_translated=False,
                error=f"Sarvam AI translation timed out after {self.timeout}s."
            )
        except Exception as exc:
            logger.error(f"Unexpected error communicating with Sarvam AI: {exc}", exc_info=True)
            return TranslateResponse(
                success=False,
                original_text=raw_text,
                translated_text=raw_text,
                source_language_code=None,
                is_translated=False,
                error=f"Sarvam AI translation error: {str(exc)}"
            )


# Singleton instance helper
_sarvam_service: SarvamTranslationService | None = None

def get_sarvam_service() -> SarvamTranslationService:
    global _sarvam_service
    if _sarvam_service is None:
        _sarvam_service = SarvamTranslationService()
    return _sarvam_service
