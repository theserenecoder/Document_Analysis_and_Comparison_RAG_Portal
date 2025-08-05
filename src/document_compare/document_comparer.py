import sys
from dotenv import load_dotenv
import pandas as pd
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from models.model import *
from prompts.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser


class DocumentComparerLLM:
    
    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(__file__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser
    
    def compare_documents(self):
        '''
        Compares two documents and returns a structured comparision.
        '''
        pass
    
    def _format_response(self):
        '''
        Format the response from the LLM into a structured format.
        '''
        pass