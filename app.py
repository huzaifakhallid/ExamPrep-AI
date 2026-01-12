import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from src.ingest import load_document
from src.preprocess import clean_text, chunk_text
from src.models import VectorDB
from src.llm_engine import generate_scenario_mcqs, generate_summary

app = FastAPI(title="ExamPrep AI")

# Global Vector DB instance
db = VectorDB()

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    request_type: str  # "summary" or "quiz"
    context_text: str = None 

@app.get("/")
def home():
    return {"message": "ExamPrep AI API is running!"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    print(f"Processing {file.filename}...")
    raw_text = load_document(file_path)
    
    if not raw_text:
        return {"error": "Could not extract text from file."}
    
    cleaned_text = clean_text(raw_text)
    chunks = chunk_text(cleaned_text)
    
    db.create_index(chunks)
    
    return {
        "filename": file.filename,
        "chunks_processed": len(chunks),
        "message": "File processed and indexed successfully."
    }

@app.post("/generate")
async def generate_content(request: QueryRequest):
    if db.index is None:
        return {"error": "No documents indexed. Please upload a file first."}
    
    context_chunks = db.metadata[:3] 
    context = "\n\n".join(context_chunks)
    
    response_text = ""
    
    if request.request_type == "quiz":
        print("Generating Quiz...")
        response_text = generate_scenario_mcqs(context)
        
    elif request.request_type == "summary":
        print("Generating Summary...")
        response_text = generate_summary(context)
        
    else:
        return {"error": "Invalid request_type. Use 'quiz' or 'summary'."}
        
    return {"result": response_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)