"""
Document Ingestion API — endpoints for uploading and extracting tender / procurement documents.

Design Principles (Run 6A):
- PDF validation: strictly validates file extension, magic bytes, and file size limits (<= 20 MB).
- Safe parsing: delegating extraction entirely to PDFExtractor without modifying core search/Qdrant.
- Inspectable responses: returns page-by-page extractions with warnings for image-only pages.
"""
from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.schemas.document import DocumentExtractionResponse
from app.services.pdf_extractor import PDFExtractor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Document Ingestion & Tender Processing"])

MAX_FILE_BYTES = settings.MAX_DOCUMENT_SIZE_MB * 1024 * 1024


def sanitize_filename(raw_filename: str | None) -> str:
    """
    Sanitizes user-provided filename to prevent directory traversal and invalid characters.
    """
    if not raw_filename:
        return "unnamed_document"
    # Extract basename only
    base = Path(raw_filename).name
    # Remove control characters and unsafe path tokens
    clean = re.sub(r'[^\w\s\.\-\(\)\[\]]', '_', base).strip()
    return clean or "unnamed_document"


@router.post(
    "/upload",
    response_model=DocumentExtractionResponse,
    summary="Upload procurement/tender PDF for structural text extraction",
    description=(
        "Uploads a tender or technical specification PDF document, validates format and size, "
        "and extracts text page-by-page while preserving document structure and technical specifications. "
        "Supports standard searchable PDF documents up to 20 MB."
    ),
    status_code=status.HTTP_200_OK,
)
async def upload_document(
    file: UploadFile = File(..., description="Tender or specification PDF file")
) -> DocumentExtractionResponse:
    """
    Upload and extract text from a PDF document.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided in upload."
        )

    safe_name = sanitize_filename(file.filename)

    # 1. Validate file extension
    if not safe_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: '{safe_name}'. Only PDF documents (.pdf) are supported in this phase."
        )

    # 2. Read file content and validate size
    try:
        content = await file.read()
    except Exception as e:
        logger.error("Failed to read uploaded file: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file stream."
        )

    file_size = len(content)
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    if file_size > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File size ({file_size / (1024 * 1024):.1f} MB) exceeds maximum allowed "
                f"limit of {settings.MAX_DOCUMENT_SIZE_MB} MB."
            )
        )

    # 3. Validate PDF magic bytes (%PDF-)
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format: File header is missing the standard PDF signature ('%PDF-')."
        )

    # 4. Generate safe document ID
    doc_id = str(uuid.uuid4())

    # 5. Extract text page-by-page using PDFExtractor
    try:
        extraction_result = PDFExtractor.extract_from_bytes(
            pdf_bytes=content,
            filename=safe_name,
            document_id=doc_id,
            content_type=file.content_type or "application/pdf",
        )
    except Exception as exc:
        logger.error("PDF extraction crashed for document %s: %s", safe_name, exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during PDF text extraction: {str(exc)}"
        )

    # 6. Optional: Persist raw document safely to disk if storage directory exists
    try:
        storage_dir = settings.DOCUMENT_STORAGE_PATH
        storage_dir.mkdir(parents=True, exist_ok=True)
        save_path = storage_dir / f"{doc_id}.pdf"
        save_path.write_bytes(content)
    except Exception as save_err:
        logger.warning("Could not persist raw PDF to data/documents (non-critical): %s", save_err)

    return extraction_result
