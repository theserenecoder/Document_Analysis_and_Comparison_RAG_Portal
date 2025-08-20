import os
import sys
from dotenv import load_dotenv
import streamlit as st

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.vectorstores import FAISS
from langchain_core.runnables.history import RunnableWithMessageHistory

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompts.prompt_library import PROMPT_REGISTRY
from model.models import PromptType


class ConversationRAG:
    
    def __init__(self):
        try:
            pass
        except Exception as e:
            pass
        
    def load_retriever_from_faiss(self):
        try:
            pass
        except Exception as e:
            pass
        
    def invoke(self):
        try:
            pass
        except Exception as e:
            pass
        
    def _load_llm(self):
        try:
            pass
        except Exception as e:
            pass
    
    @staticmethod
    def _format_docs(docs):
        try:
            pass
        except Exception as e:
            pass
        
    def _build_lcel_chain(self):
        try:
            pass
        except Exception as e:
            pass