"""
API routes for CSV/JSON file ingestion upload.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.utils.security import verify_api_key
from app.utils.storage import storage_client
from app.tasks.sync import process_uploaded_file_task

router = APIRouter(prefix="/upload", tags=["upload"])

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

    # Verify that the store_id matches the API key's store
    if str(store.id) != store_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key does not match store"
        )

    # Determine file type
    filename = file.filename.lower()
    if filename.endswith(".csv"):
        file_type = "csv"
    elif filename.endswith(".json"):
        file_type = "json"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Only .csv and .json files are allowed."
        )

    # Read file content
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read upload file: {str(e)}"
        )

    # Upload to storage client (MinIO with local filesystem fallback)
    try:
        file_key = storage_client.upload_file(contents, f"{store_id}_{file.filename}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Trigger background parsing & indexing Celery task
    process_uploaded_file_task.delay(store_id, file_key, file_type)

    return {
        "status": "success",
        "message": "File uploaded successfully. Ingestion task started in background.",
        "file_key": file_key,
        "file_type": file_type
    }
