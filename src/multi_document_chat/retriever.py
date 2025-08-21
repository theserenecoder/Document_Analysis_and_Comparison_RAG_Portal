import os
import sys
from operator import itemgetter
import streamlit as st

from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import FAISS

from utils.model_loader import ModelLoader
from logger.custom_logger import CustomLogger
from exception.custom_exception import DocumentPortalException
from prompts.prompt_library import PROMPT_REGISTRY
from model.models import PromptType


class ConversationRAG:
    
    def __init__(self, session_id:str, retriever =None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            ## loading session id
            self.session_id = session_id
            ## llm
            self.llm = self._load_llm()
            ## Prompt
            self.contextualize_prompt = PROMPT_REGISTRY(PromptType.CONTEXTUALIZE_QUESTION.value)
            self.qa_prompt = PROMPT_REGISTRY(PromptType.CONTEXT_QA.value)
            ## loading retriever
            if retriever is None:
                raise ValueError("Retriever is None")
            self.retriever = retriever
            ## build lcel chain
            self._build_lcel_chain()
            
            self.log.info("ConversationalRAG Initialized", session_id = self.session_id)
            
        except Exception as e:
            self.log.error("Failed to initialised ConversationalRAG", error = str(e))
            raise DocumentPortalException("Initialization error in ConversationalRAG", sys)
        
    def load_retriever_from_faiss(self, index_path:str):
        """Load a FAISS vectostore from disk and convert to retriever
        """
        try:
            ## load embedding model
            embedding = ModelLoader().load_embedding_model()
            ## check if path is a directory path
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            ## loading index
            vectore_store = FAISS.load_local(index_path, embedding, allow_dangerous_deserialization=True)
            self.retriever = vectore_store.as_retriever(search_type ='similarity', search_kwargs={"k":5})
            self.log.info("Loaded retriever from FAISS index", index_path=index_path)
            
            self._build_lcel_chain()
            
            return self.retriever
            
        except Exception as e:
            self.log.error("Failed to load retriever from FAISS", error=str(e))
            raise DocumentPortalException("Loading error in CoversationalRag",sys)
        
    def invoke(self):
        try:
            pass
        except Exception as e:
            self.log.error("Failed to invoke CoversationalRag", error=str(e))
            raise DocumentPortalException("Invocation error in CoversationalRag",sys)
        
    def _load_llm(self):
        try:
            ## load llm
            llm = ModelLoader().load_llm()
            ## check if llm or not
            if not llm:
                raise ValueError("LLM could not be loaded")
            ## logging
            self.log.info("LLM loaded successfully", session_id = self.session_id)
            
            return llm
        except Exception as e:
            self.log.error("Failed to Load llm in CoversationalRag", error=str(e))
            raise DocumentPortalException("LLM loading error in CoversationalRag",sys)
    
    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)
        
    def _build_lcel_chain(self):
        try:
            ## Will rewrite question based on our chat history
            question_rewriter = (
                {
                    "input":itemgetter("input"),
                    "chat_history":itemgetter("chat_history")
                }
                | self.contextualize_prompt
                | self.llm
                | StrOutputParser() 
            )
            ## Retrieve docs for rewriting questions
            retrieve_docs = question_rewriter | self.retriever | self._format_docs
            
            ## feed context + original input + chat history into answer prompt
            self.chain = (
                {
                    "context": retrieve_docs,
                    "input" : itemgetter("input"),
                    "chat_history": itemgetter("chat_history")
                }
                | self.qa_prompt
                | self.llm
                | StrOutputParser()
            )
            
            self.log.info("LECL graph build successfully", session_id = self.session_id)
            
        except Exception as e:
            self.log.error("Failed to build LCEL chain", error=str(e))
            raise DocumentPortalException("Chain building error in CoversationalRag",sys)