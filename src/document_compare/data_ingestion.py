import sys
from pathlib import Path
import fitz
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException

class DocumentIngestion:
    
    def __init__(self, base_dir):
        ## Initializing our custom logger
        self.log = CustomLogger().get_logger(__name__)
        ## creating path of our directory
        self.base_dir = Path(base_dir)
        ## creating a directory if doesn't exists
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def delete_existing_files(self):
        """
        Deletes existing files at the specified paths
        """
        try:
            ## check if directory path existis and path is a directory
            if self.base_dir.exists() and self.base_dir.is_dir():
                ## iterating over files in directory
                for file in self.base_dir.iterdir():
                    ## removing/unlining the file
                    file.unlink()
                    self.log.info("File deleted.", path=str(file))
                    
                self.log.info("Directory cleaned",directory=str(self.base_dir))
                
        except Exception as e:
            self.log.error(f"Error deleting existing files: {e}")
            raise DocumentPortalException("An error occured while deleting existing files.",sys)
    
    def save_uploaded_files(self, reference_file, actual_file):
        """
        Save uploaded files to a specified directory
        """
        try:
            ## deleting any existing file
            self.delete_existing_files()
            self.log.info("Existing file deleted successfully")
            
            ## updated file
            ref_path =self.base_dir/reference_file.name
            ## original file
            act_path = self.base_dir/reference_file.name
            
            ## raise value error if not pf file
            if not reference_file.name.endswith(".pdf") or not actual_file.name.endswith(".pdf"):
                raise ValueError("Only PDF files are allowed")
            
            ## writing both the files
            with open(ref_path,'wb') as file:
                file.write(reference_file.getbuffer())
                
            with open(act_path,'wb') as file:
                file.write(actual_file.getbuffer())
                
            self.log.info(f"Files saved.", reference=str(ref_path), actual=str(act_path))
                
            
            
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
        
    def combine_document(self) ->str:
        try:
            content_dict = {}
            doc_parts = []
            
            ## iterating over files and storing them as dict
            for filename in sorted(self.base_dir.iterdir()):
                if filename.is_file() and filename.suffix ==".pdf":
                    content_dict[filename.name] = self.read_pdf(filename)
            ## saving the filename and content as list      
            for file, content in content_dict.items():
                doc_parts.append(f"Document: {file}\n{content}")
            
            ## combining the files
            combine_text = "\n\n".join(doc_parts)
            self.log.info("Document Combined", count = len(doc_parts))
            
            return combine_text
            
        except Exception as e:
            self.log.error(f"Error combining documents: {e}")
            raise DocumentPortalException("An error ocurred while combining the documents.",sys)