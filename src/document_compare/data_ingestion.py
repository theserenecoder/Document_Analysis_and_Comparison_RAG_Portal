import sys
from pathlib import Path
import fitz
import uuid
from datetime import datetime, timezone
import os


from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentIngestion:
    """Handles saving, reading and combining of PDF's for comparision with session-based versioning.
    """
    
    def __init__(self, base_dir: str="data\\document_compare", session_id = None):
        ## Initializing our custom logger
        self.log = CustomLogger().get_logger(__name__)
        ## creating path of our directory
        self.base_dir = Path(base_dir)
        ## creating a session id
        self.session_id = session_id or f"session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        ## creating session path
        self.session_path = self.base_dir/self.session_id
        ## creating a directory if doesn't exists
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.log.info("Document Ingestion Initialized", session_path=str(self.session_path))
    
    def save_uploaded_files(self, reference_file, actual_file):
        """
        Save uploaded files to a specified directory
        """
        try:          
            ## updated file
            ref_path =self.session_path/reference_file.name
            ## original file
            act_path = self.session_path/actual_file.name
            
            ## raise value error if not pf file
            if not reference_file.name.lower().endswith(".pdf") or not actual_file.name.lower().endswith(".pdf"):
                raise ValueError("Only PDF files are allowed")
            
            ## writing both the files
            with open(ref_path,'wb') as file:
                file.write(reference_file.getbuffer())
                
            with open(act_path,'wb') as file:
                file.write(actual_file.getbuffer())
                
            self.log.info(f"Files saved.", reference=str(ref_path), actual=str(act_path), session=self.session_id)
                
            return ref_path, act_path
            
        except Exception as e:
            self.log.error(f"Error saving uploaded file: {e}")
            raise DocumentPortalException("An error occured while saving the uploaded file.",sys)
    
    def read_pdf(self, pdf_path:Path)->str:
        try:
            ## open the file which has been saved
            with fitz.open(pdf_path) as doc:
                ## if file is encrypted raise value error
                if doc.is_encrypted:
                    raise ValueError(f"PDF is encrypted: {pdf_path.name}")
                
                ## loading text of each page of the document
                all_text = []
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        all_text.append(f"\n --- Page {page_num + 1} --- \n{text}")
                
                
            self.log.info("PDF read successfully.",file=str(pdf_path), page = len(all_text))    
            return "\n".join(all_text)
                
        except Exception as e:
            self.log.error(f"Error reading PDFs: {e}")
            raise DocumentPortalException("An error ocurred while reading the PDFs.",sys)
        
    def combine_documents(self) ->str:
        """Combine content of all PDFs in session folder into a single string.
        """
        try:
            #content_dict = {}
            doc_parts = []
            
            ## iterating over files and storing them as dict
            for file in sorted(self.session_path.iterdir()):
                if file.is_file() and file.suffix.lower() ==".pdf":
                    content = self.read_pdf(file)
                    doc_parts.append(f"Document: {file.name}\n{content}")
            
            ## combining the files
            combine_text = "\n\n".join(doc_parts)
            self.log.info("Document Combined", count = len(doc_parts), session=self.session_id)
            
            return combine_text
            
        except Exception as e:
            self.log.error(f"Error combining documents", error=str(e), session=self.session_id)
            raise DocumentPortalException("An error ocurred while combining the documents.",sys)
        
        
    def cleaned_old_session(self, keep_latest: int = 3):
        """Optional method to delete older session folder, keeping only the latest N
        """
        try:
            session_folders = sorted(
                [f for f in self.base_dir.iterdir() if f.is_dir()],
                reverse=True
            )
            
            for folder in session_folders[keep_latest :]:
                for file in folder.iterdir():
                    file.unlink()
                folder.rmdir()
                self.log.info("Old session folder deleted", path = str(folder))
                
        except Exception as e:
            self.log.error(f"Error cleaning old sessions", error=str(e))
            raise DocumentPortalException("Error cleaning old sessions.",sys)