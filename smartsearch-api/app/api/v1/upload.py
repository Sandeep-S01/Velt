"""
API routes for CSV/JSON file ingestion upload.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.security import (
    get_current_active_user,
    get_owned_store,
    require_api_key_scope,
    verify_api_key,
)
from app.utils.storage import storage_client
from app.tasks.sync import process_uploaded_file_task
import uuid

router = APIRouter(prefix="/upload", tags=["upload"])
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    "csv": {"text/csv", "application/csv", "application/vnd.ms-excel"},
    "json": {"application/json", "text/json"},
}


async def _store_upload(store_id: str, file: UploadFile):
    filename = (file.filename or "").lower()
    if filename.endswith(".csv"):
        file_type = "csv"
    elif filename.endswith(".json"):
        file_type = "json"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only .csv and .json files are allowed.",
        )

    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES[file_type]:
        raise HTTPException(status_code=400, detail="File content type does not match extension")

    try:
        chunks = []
        total_bytes = 0
        while chunk := await file.read(1024 * 1024):
            total_bytes += len(chunk)
            if total_bytes > MAX_UPLOAD_BYTES:
                raise HTTPException(status_code=413, detail="Upload exceeds 10 MB limit")
            chunks.append(chunk)
        contents = b"".join(chunks)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read upload file",
        ) from exc

    try:
        object_name = f"{store_id}/{uuid.uuid4().hex}.{file_type}"
        file_key = storage_client.upload_file(contents, object_name)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save uploaded file",
        ) from exc

    process_uploaded_file_task.delay(store_id, file_key, file_type)
    return {
        "status": "success",
        "message": "File uploaded successfully. Ingestion task started in background.",
        "file_key": file_key,
        "file_type": file_type,
    }

@router.post("")
async def upload_product_file(
    store_id: str = Form(..., description="The ID of the store to ingest products into"),
    file: UploadFile = File(..., description="The CSV or JSON file containing products"),
    db: Session = Depends(get_db),
    api_key_info: tuple = Depends(verify_api_key)
):
    """
    Upload a CSV or JSON file containing products for bulk ingestion.
    Requires a valid API key authorized for the target store.
    """
    api_key, store = api_key_info
    require_api_key_scope(api_key, "ingest")

    # Verify that the store_id matches the API key's store
    if str(store.id) != store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not match store"
        )

    return await _store_upload(store_id, file)


@router.post("/dashboard")
async def upload_product_file_from_dashboard(
    store_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Upload a catalog using dashboard authentication instead of a private API key."""
    get_owned_store(db, store_id, current_user.id)
    return await _store_upload(store_id, file)
