import os
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from model.models import *
from prompts.prompt_library import PROMPT_REGISTRY

from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser


class DocumentAnalyzer:
    """Analyze document using a pre-trained model.
    Automatically logs all action and supports session-based organization.
    """
    
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()
            
            self.parser = JsonOutputParser(pydantic_object=Metadata)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
            
            self.prompt = PROMPT_REGISTRY['document_analysis']
            
            self.log.info("DocumentAnalyzer initialized successfully")
            
        except Exception as e:
            self.log.error("Error initializing DocumentAnalyzer: {e}")
            raise DocumentAnalyzer("Error initializing DocumentAnalyzer",e)
    
    def analyze_document(self, document_text:str):
        """Analyze a document's text and extract structured metadata & summary.
        """
        try:
            ## creating a chain which has prompt, llm and parser
            chain = self.prompt | self.llm | self.parser
            
            self.log.info("Metadata analysis chain initialized.")
            
            ## invoking the chain and getting th
            response = chain.invoke(
                {
                    "format_instructions":self.parser.get_format_instructions(),
                    "document_text":document_text
                }
            )
            
            self.log.info("Metadata extraction successful", keys = list(response.keys()))
            
            return response
            
        except Exception as e:
            self.log.error("Metadata analysis Failed: {e}")
            raise DocumentAnalyzer("Metadata analysis Failed",e)