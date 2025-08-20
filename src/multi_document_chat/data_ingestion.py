import uuid
from pathlib import Path
import sys
from datetime import datetime, timezone

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, Mar
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader


class DocumentIngestor:
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx','.txt','.md'}
    
    def __init__(self, temp_dir:str = "data/multi_document_chat", faiss_dir:str = 'faiss_index', session_id: str|None = None):
        try:
            ## defining custom logger
            self.log =  CustomLogger().get_logger(__name__)
            
            ## defining temp directory
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
            
            ## defining faiss directory
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            
            ## sessionized path
            self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            ## creating session temp directory
            self.session_temp_dir = self.temp_dir / self.session_id
            self.session_temp_dir.mkdir(parents=True,exist_ok=True)
            ## creating session faiss directory
            self.session_faiss_dir = self.faiss_dir / self.session_id
            self.session_faiss_dir.mkdir(parents=True,exist_ok=True)
            
            ## loading model
            self.model_loder = ModelLoader()
            
            ## logging
            self.log.info(
                "DocumentIngestor initialized",
                temp_base = str(self.temp_dir),
                faiss_base = str(self.faiss_dir),
                session_id = self.session_id,
                temp_path = str(self.session_temp_dir),
                faiss_path = str(self.session_faiss_dir)
            )
            
            
            
        except Exception as e:
            self.log.error("Failed to initialize DocumentIngestor", error = str(e))
            raise DocumentPortalException("Initialization error in DocumentIngestor", sys)
        
        
    def ingest_files(self, uploaded_files):
        try:
            documents = []
            ## iterating over all the files
            for uploaded_file in uploaded_files:
                ## extracting the suffix/extension of the file like .pdf, .txt etc
                ext = Path(uploaded_files.name).suffix.lower()
                ## checking if the extension in supported types
                if ext not in self.SUPPORTED_EXTENSIONS:
                    self.log.warning("Unsupported file skipped", filename = uploaded_file.name)
                    continue
                ## defining unique file name
                unique_filename = f"{uuid.uuid4().hex[:8]}{ext}"
                temp_path = self.session_temp_dir / unique_filename
                ## writing in the session file
                with open(temp_path,'wb') as file:
                    file.write(uploaded_file.read())
                
                ## logging
                self.log.info("File saved for ingestion", filename = uploaded_file.name, saved_as=str(temp_path), session_id = self.session_id)
                
                ## loading documents as per extension
                if ext == '.pdf':
                    loader = PyPDFLoader(str(temp_path))
                elif ext == '.txt':
                    loader = TextLoader(str(temp_path), encoding='utf-8')
                elif ext == '.docx':
                    loader = Docx2txtLoader(str(temp_path))
                else:
                    self.log.warning("Unsupported file type encountered", filename = uploaded_file.name)
                    continue
                
                ## reading the documents and appending in list
                docs = loader.load()
                documents.extend(docs)
                
                ## if no documents in list raising error
                if not documents:
                    raise DocumentPortalException("No valid documents loaded", sys)
                
            self.log.info("All documents loaded", total_docs = len(documents), session_id = self.session_id)
                
            return self._create_retriever(documents)
                
        except Exception as e:
            self.log.error("Failed to ingest file", error = str(e))
            raise DocumentPortalException("Ingestion error in DocumentIngestor", sys)
        
    def _create_retriever(self, documents):
        try:
            ## initializing splitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap = 300)
            ## split documents into chunks
            chunks = splitter.split_documents(documents)
            ## logging
            self.log.info("Documents split into chunks", total_chunks = len(chunks), session_id = self.session_id)
            
            ## loading embedding model
            embedding_model = self.model_loader.load_embedding_model()
            
            ## defining vector store
            vector_store = FAISS.from_documents(
                documents=chunks,
                embedding=embedding_model
            )
            
            ## save faiss vectore store
            vector_store.save_local(str(self.session_faiss_dir))
            self.log.info("FAISS index saved to disk",path = str(self.session_faiss_dir), session_id =self.session_id)
            
            ## creating retriever
            retriever = vector_store.as_retriever(search_type = "similarity",search_kwargs={"k":5})
            self.log.info("FAISS retriever created and ready to use", session_id = self.session_id)
            
            return retriever
            
            
        except Exception as e:
            self.log.error("Failed to create retriever", error=str(e))
            raise DocumentPortalException("Retrieval error in DocumentIngestor", sys)