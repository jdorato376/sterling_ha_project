
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/sterling/assistant")
async def sterling_assistant(request: Request):
    body = await request.json()
    query = body.get("query", "")
    return {"response": f"Sterling received: {query}"}
