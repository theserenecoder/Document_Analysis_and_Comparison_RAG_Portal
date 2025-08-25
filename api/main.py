from fastapi import FastAPI, UploadFile, File,Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any

app = FastAPI(title = "Document Portal API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## serving static and the templates
app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request : Request):
    ## renders template/index.html
    return templates.TemplateResponse("index.html",{"request": request})

@app.get("/health")
def health() -> Dict[str,str]:
    return {"status":"ok", "service": "document-portal"}
    
    
@app.post("/analyze")
async def analyze_documents(file: UploadFile = File(...)) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    
    
@app.post("/compare")
async def compare_documents(reference: UploadFile = File(...), actual: UploadFile = File(...)) -> Any:
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e}")
    
    
@app.post("/chat/index")
async def chat_built_index():
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")
    

@app.post("chat/query")
async def chat_query():
    try:
        pass
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")