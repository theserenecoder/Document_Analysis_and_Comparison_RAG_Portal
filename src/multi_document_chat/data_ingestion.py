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

class DocumentIngestor:
    
    def __init__(self):
        try:
            pass
        except Exception as e:
            pass
        
        
    def ingest_files(self):
        try:
            pass
        except Exception as e:
            pass
        
    def create_retriever(self, documents):
        try:
            pass
        except Exception as e:
            pass