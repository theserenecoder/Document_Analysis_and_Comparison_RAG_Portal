import os
import sys
from dotenv import load_dotenv

from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from utils.config_loader import load_config

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_openai import OpenAIEmbeddings, ChatOpenAI



class ModelLoader():
    def __init__(self):
        """A utility class to load embedding models and LLM models.
        """
        self.log = CustomLogger().get_logger(__name__)
        load_dotenv()
        ## check that environment variables are loaded
        self._validate_env()
        ## loading all the config
        self.config = load_config()
        ## logging success
        self.log.info("Configuration loaded successfully", config_keys=list(self.config.keys()))
    
    def _validate_env(self):
        '''A function to validate environment variable and ensures API key exists'''
        ## first we will define all the keys which we know should be loaded
        required_vars=['GOOGLE_API_KEY','GROQ_API_KEY','OPENAI_API_KEY']
        ## get all the api keys from the environment
        self.api_keys = {key:os.getenv(key) for key in required_vars}
        ## list out any api key which are missing
        missing = [k for k,v in self.api_keys.items() if not v]
        ## if any api key is missing will log and raise the custom exception
        if missing:
            self.log.error("Missing environmentvariables", missing_vars = missing)
            raise DocumentPortalException("Missing environment variables", sys)
        self.log.info("Environment variables validated", available_keys=[k for k in self.api_keys if self.api_keys[k]])
    
    def load_embedding_model(self):
        '''Load and return embedding model'''
        try:
            self.log.info('Loading the embedding model...')
            model_name = self.config['embedding_model']['model_name']
            return OpenAIEmbeddings(model=model_name)
        except Exception as e:
            self.log.error('Error loading embedding model', error=str(e))
            raise DocumentPortalException('Failed to load embedding model',sys)
    
    def load_llm(self):
        '''Load the LLM models dynamically based on provider in cofig and return it'''
        ## loading the complete llm block from yaml file
        llm_block = self.config['llm']
        
        self.log.info("Loading LLM...")
        
        ## If we have defined the LLM provider it will take that else it will take google
        provider_key = os.getenv('LLM_PROVIDER','openai')
        
        if provider_key not in llm_block:
            self.log.error('LLM provider not found in config', provider_key = provider_key)
            raise ValueError(f"Provider '{provider_key}' not found in cofig")
        
        llm_config = llm_block[provider_key]
        provider = llm_config.get('provider')
        model_name = llm_config.get('model_name')
        temperature = llm_config.get('temperature')
        max_tokens = llm_config.get('max_output_tokens')
        
        self.log.info("Loading LLM", provider=provider,model_name=model_name, temperature=temperature, max_tokens= max_tokens)
        
        if provider == 'openai':
            llm = ChatOpenAI(
                model = model_name,
                temperature=temperature,
                max_tokens = max_tokens
            )
            return llm
        
        elif provider =='google':
            llm = ChatGoogleGenerativeAI(
                model = model_name,
                temperature=temperature,
                max_output = max_tokens
            )
            return llm
        
        else:
            self.log.error("Unsupported LLM provider", provider = provider)
            raise ValueError(f'Unsupported LLM Provider : {provider}')
        

if __name__=='__main__':
    loader = ModelLoader()
    
    ## test embedding model
    embeddings = loader.load_embedding_model()
    print('\n')
    print(f"Embedding model Loaded : {embeddings}")
    
    ## test the model loader
    # result = embeddings.embed_query("Hello how are you")
    # print("\n")
    # print(f"Embedding result: {result}")
    
    ## test the llm loader
    llm = loader.load_llm()
    print('\n')
    print(f"LLM Model loaded : {llm}")
    
    ## test the model loader
    result_llm = llm.invoke("Hello how are you")
    print("\n")
    print(f"LLM Result: {result_llm}")