from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from modules.vertex_integration.vertex_client import predict

app = FastAPI()

class Query(BaseModel):
    query: str

@app.post("/assistant")
async def assistant(q: Query):
    try:
        response = predict(q.query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
