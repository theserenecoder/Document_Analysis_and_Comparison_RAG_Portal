import sys
from dotenv import load_dotenv
import pandas as pd
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from model.models import *
from prompts.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser
import pandas as pd


class DocumentComparerLLM:
    
    def __init__(self):
        load_dotenv()
        ## initializing custom logger
        self.log = CustomLogger().get_logger(__file__)
        ## initializing model
        self.loader = ModelLoader()
        ## loading model
        self.llm = self.loader.load_llm()
        ## Output parser
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm = self.llm)
        ## Loading Prompt
        self.prompt = PROMPT_REGISTRY['document_comparision']
        ## Defining the chain
        self.chain = self.prompt | self.llm | self.parser 
        ## logging success
        self.log.info("\nDocument Comparer LLM initialized with model and parser", model=self.llm)
    
    def compare_documents(self, combined_docs: str) -> pd.DataFrame:
        '''
        Compares two documents and returns a structured comparision.
        '''
        try:
            inputs = {
                "combined_docs" : combined_docs,
                "format_instruction" : self.parser.get_format_instructions()
            }
            self.log.info("Starting document comparision", inputs=inputs)
            
            response = self.chain.invoke(inputs)
            self.log.info("Document comparision completed", response_preview=str(response)[:100])
            
            return self._format_response(response)
        
        except Exception as e:
            self.log.error(f"Error in compare_documents", error=str(e))
            raise DocumentPortalException("An error occured while comparing documents.", sys)
    
    def _format_response(self,response_parsed:list[dict])->pd.DataFrame:
        '''
        Format the response from the LLM into a structured format.
        '''
        try:
            ## converting response into dataframe
            df = pd.DataFrame(response_parsed)
            self.log.info("Response formatted into Dataframe", dataframe=df)
            return df
            
        except Exception as e:
            self.log.error(f"Error formatting response into DataFrame", error=str(e))
            raise DocumentPortalException("Error formatting response.",sys)