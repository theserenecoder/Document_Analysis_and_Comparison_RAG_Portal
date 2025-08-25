from fastapi import FastAPI, UploadFile, File,Form, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
from pathlib import Path
import os

from src.document_ingestion.data_ingestion import (
    DocumentHandler, 
    DocumentComparator, 
    FaissManager,
    ChatIngestor
)

from src.document_analyzer.data_analysis import DocumentAnalyzer
from src.document_compare.document_comparer import DocumentComparerLLM
from src.document_chat.retrieval import ConversationRAG

BASE_DIR = Path(__file__).resolve().parent.parent



app = FastAPI(title = "Document Portal API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## serving static and the templates
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@app.get("/", response_class=HTMLResponse)
async def serve_ui(request : Request):
    ## renders template/index.html
    return templates.TemplateResponse("index.html",{"request": request})

@app.get("/health")
def health() -> Dict[str,str]:
    return {"status":"ok", "service": "document-portal"}

class FastAPIFileAdapter:
    """Adapt FastAPI UploadFile -> .name + .getbuffer() API"""
    
    def __init__(self, uf: UploadFile):
        self._uf = uf
        self.name = uf.filename
        
    def getbuffer(self) -> bytes:
        self._uf.file.seek(0)
        return self._uf.file.read()

def _read_pdf_via_handler(handler: DocumentHandler, path:str) ->str:
    """Utility function to read pdf via DocumentHandler
    """
    try:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading PDF : {str(e)}")

@app.post("/analyze")
async def analyze_documents(file: UploadFile = File(...)) -> Any:
    try:
        ## object of document handler
        dh = DocumentHandler()
        ## saving the uploaded file
        save_path = dh.save_pdf(FastAPIFileAdapter(file))
        ## reading the file content
        text = _read_pdf_via_handler(dh, save_path)
        
        ## object of document analyzer
        analyzer = DocumentAnalyzer()
        ## analyzing the document
        result = analyzer.analyze_document(text)
        
        ## returning the response as JSON response
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")
    
    
@app.post("/compare")
async def compare_documents(reference: UploadFile = File(...), actual: UploadFile = File(...)) -> Any:
    try:
        dc = DocumentComparator()
        
        ref_path, act_path = dc.save_uploaded_files(FastAPIFileAdapter(reference), FastAPIFileAdapter(actual))
        
        _ = ref_path, act_path
        combined_test = dc.combine_documents()
        
        comp = DocumentComparerLLM()
        df = comp.compare_documents(combined_test)
        
        return {'rows': df.to_dict(orient='records'), "session_id": dc.session_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e}")
    
    
@app.post("/chat/index")
async def chat_built_index(
        files: List[UploadFile] = File(...),
        session_id: Optional[str] = Form(None),
        use_session_dirs: bool = Form(True),
        chunk_size: int = Form(1000),
        chunk_overlap: int = Form(200),
        k: int = Form(5)
) -> Any:
    try:  
        wrapped = [FastAPIFileAdapter(f) for f in files]
        ci = ChatIngestor(
            temp_base = UPLOAD_BASE,
            faiss_base = FAISS_BASE,
            use_session_dirs=use_session_dirs,
            session_id = session_id or None,
        )
        
        ci.built_retriever(wrapped, chunk_size=chunk_size, chunk_overlap=chunk_overlap, k=k)
        
        return {"session_id":ci.session_id, "k":k, "use_session_dirs": use_session_dirs}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")
    

@app.post("chat/query")
async def chat_query(
    question: str = Form(...),
    session_id: Optional[str]  =Form(None),
    use_session_dirs: bool = Form(True),
    k: int = Form(5),
)->Any:
    try:
        if use_session_dirs and not session_id:
            raise HTTPException(status_code=400, detail="session_id is required when use_session_dirs is True")
        
        ## Prepare FAISS index path
        index_path = os.path.join(FAISS_BASE, session_id) if use_session_dirs else FAISS_BASE
        if not os.path.isdir(index_path):
            raise HTTPException(status_code=400, detail=f"FAISS index not found at {index_path}")
        
        ## Initialize LCEL-style RAG pipeline
        rag = ConversationRAG(session_id=session_id)
        rag.load_retriever_from_faiss(index_path)
        
        response = rag.invoke(question, chat_history=[])
        
        return {
            "answer": response,
            "session_id":session_id,
            "k":k,
            "engine": "LCEL-RAG"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")