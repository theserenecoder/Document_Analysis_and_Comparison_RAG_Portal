import os
import sys
from dotenv import load_dotenv

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompts.prompt_library import PROMPT_REGISTRY
from model.models import PromptType


class ConversationalRAG:
    def __init__(self, session_id: str, retriever) ->None:
        try:
            self.log = CustomLogger().get_logger()
            
        except Exception as e:
            self.log.error("Error initializing ConversationalRAG", error=str(e),session_id = session_id)
            raise DocumentPortalException("Failed to initialize ConversationalRAG", sys)
            
    def _load_llm(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error loading LLM via ModelLoader", error=str(e))
            raise DocumentPortalException("Failed to load llm", sys)
        
    def _get_session_history(self, session_id:str):
        try:
            pass
        except Exception as e:
            self.log.error("Failed to access session history", error=str(e), session_id=session_id)
            raise DocumentPortalException("Failed to retrieve session history", sys)
        
    def load_retriever(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error loading retriever from FAISS", error=str(e))
            raise DocumentPortalException("Failed to load retriever from FAISS", sys)
        
    def invoke(self):
        try:
            pass
        except Exception as e:
            self.log.error("Error invoking Conversational RAG", error=str(e), session_id = session_id)
            raise DocumentPortalException("Failed to invoking Conversational RAG", sys)