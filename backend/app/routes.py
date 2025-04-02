from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph import app as langgraph_app
from app.document_prep import ingest_data, clear_database

router = APIRouter()

class URLList(BaseModel):
    urls: list[str]

class QueryRequest(BaseModel):
    question: str

@router.post("/query")
async def get_answer(request: QueryRequest):
    inputs = {"question": request.question}
    final_response = None
    print("request---------------->",request)
    for output in langgraph_app.stream(inputs):
        for key, value in output.items():
            final_response = value.get("generation", None)
    print("final response---------------->",final_response)
    if final_response is not None:
        final_response = final_response.content
    response = JSONResponse(content={"answer": final_response or "No relevant answer found."})
    response.headers["Access-Control-Allow-Origin"] = "*"
    print("response---------------->",response)
    return response

@router.post("/ingest")
async def ingest_data_endpoint(request: URLList):
    try:
        ingest_data(request.urls)
        response = JSONResponse(content={"message": "Data ingestion successful."})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting data: {str(e)}")

@router.post("/clear")
async def clear_database_endpoint():
    try:
        clear_database()
        response = JSONResponse(content={"message": "Database cleared successfully."})
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing database: {str(e)}")
