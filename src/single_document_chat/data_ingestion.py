import uuid
from pathlib import Path
import sys
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.model_loader import ModelLoader
from datetime import datetime, timezone
import uuid

class SingleDocIngestor:
    def __init__(self,data_dir:str = "data/single_document_chat", faiss_dir:str = "faiss_index"):
        try:
            self.log = CustomLogger().get_logger()
            ## defining data directory path
            self.data_dir = Path(data_dir)
            ## when parent =True it will create parent directories as well if missing
            self.data_dir.mkdir(parents=True, exist_ok=True)
            ## vector store directory
            self.faiss_dir = Path(faiss_dir)
            self.faiss_dir.mkdir(parents=True, exist_ok=True)
            ## loading model loader
            self.model_loader = ModelLoader()
            ## logging
            self.log.info("SingleDocIngestor Initialized", data_path=str(self.data_dir), faiss_path=str(self.faiss_dir))
            
        except Exception as e:
            self.log.error("Failed to initialize SingleDocIngestor", error=str(e))
            raise DocumentPortalException("Initialization error in SingleDocIngestor",sys)
        
    def ingest_files(self, uploaded_files):
        try:
            ## creating an empty list
            documents = []
            ## loading uploaded file
            for uploaded_file in uploaded_files:
                ## defining a random file name
                unique_filename = f"session_{datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:8]}.pdf"
                ## defining a temp file path
                temp_path = self.data_dir/unique_filename
                ## writing the file at temp path
                with open(temp_path, "wb") as file:
                    file.write(uploaded_file.read())
                self.log.info("PDF saved for ingestion", filename = uploaded_file.name)
                
                ## load the file
                loader = PyPDFLoader(temp_path)
                docs = loader.load()
                ## appending the file in document list
                documents.extend(docs)
            
            ## logging
            self.log.info("PDF files loaded", counts = len(documents))
            return self._create_retriever(documents)
            
        except Exception as e:
            self.log.error("Document ingestion failed", error=str(e))
            raise DocumentPortalException("Error during file ingestion",sys)
        
    def _create_retriever(self, documents):
        try:
            ## initializing splitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap = 300)
            ## split documents into chunks
            chunks = splitter.split_documents(documents)
            ## logging
            self.log.info("Documents split into chunks", count = len(chunks))
            
            ## loading embedding model
            embedding_model = self.model_loader.load_embedding_model()
            
            ## defining vector store
            vector_store = FAISS.from_documents(
                documents=chunks,
                embedding=embedding_model
            )
            
            ## save FAISS index
            vector_store.save_local(self.faiss_dir)
            ## logging
            self.log.info("FAISS vector store created and saved", faiss_path = str(self.faiss_dir))
            
            ## creating retriever
            retriever = vector_store.as_retriever(search_type = 'similarity', search_kwargs = {"k":5})
            ## logging
            self.log.info("Retriver created successfully", retriever = str(type(retriever)))
            
            return retriever
            
        except Exception as e:
            self.log.error("Retriever creation failed", error=str(e))
            raise DocumentPortalException("Error creating FAISS retriever",sys)