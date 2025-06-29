from fastapi import APIRouter, File, UploadFile
import time
import logging

from celery_worker import celery_app

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload-transcript", tags=["Features"])

@celery_app.task(name="process_transcript_task")
def process_transcript_task(file_content_id: str):
    """
    Simulates processing a transcript in a background task.
    """
    logger.info(f"Received task to process file with ID: {file_content_id}")
    time.sleep(10) # Simulate a long-running task
    logger.info(f"Finished processing file with ID: {file_content_id}")
    return {"status": "completed", "file_id": file_content_id}

@router.post("")
async def upload_transcript(file: UploadFile = File(...)):
    """
    Dispatches a background task to process a transcript file.
    """
    file_content_id = f"file_{int(time.time())}"
    
    process_transcript_task.delay(file_content_id)
    
    logger.info(f"Transcript uploaded and task dispatched for file ID: {file_content_id}")
    
    return {"message": "Transcript uploaded successfully. Processing will begin shortly.", "file_id": file_content_id}