from fastapi import APIRouter
from pydantic import BaseModel
from app.graph import app as langgraph_app
from app.document_prep import ingest_data, clear_database

router = APIRouter()

# Pydantic model for incoming URLs
class URLList(BaseModel):
    urls: list[str]

class QueryRequest(BaseModel):
    question: str

@router.post("/query")
async def get_answer(request: QueryRequest):
    inputs = {"question": request.question}
    final_response = None

    for output in langgraph_app.stream(inputs):
        for key, value in output.items():
            final_response = value.get("generation", None)

    return {"answer": final_response or "No relevant answer found."}



# Endpoint to ingest data from multiple URLs
@router.post("/ingest")
async def ingest_data_endpoint(request: URLList):
    try:
        # Call the function to ingest data
        ingest_data(request.urls)
        return {"message": "Data ingestion successful."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting data: {str(e)}")

# Endpoint to clear the database
@router.post("/clear")
async def clear_database_endpoint():
    try:
        # Call the function to clear the database
        clear_database()
        return {"message": "Database cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")