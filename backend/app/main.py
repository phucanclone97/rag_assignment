from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .recommender import BraFittingRAG
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    text: str

recommender = BraFittingRAG()

@app.post("/api/bra-fitting")
async def get_fitting_recommendation(query: Query):
    try:
        # Bug: No input validation
        print({"text":query.text})
        if query.text == "":
            raise HTTPException(status_code=400, detail="Query text cannot be empty")
        result = recommender.get_recommendation(query.text)
        return result
    except Exception as e:
        # Bug: Generic error handling
        raise HTTPException(status_code=500, detail=str(e.detail))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
