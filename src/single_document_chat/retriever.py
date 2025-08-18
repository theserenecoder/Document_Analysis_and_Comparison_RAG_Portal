import os
import sys
from dotenv import load_dotenv
import streamlit as st

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
            ## session id
            self.session_id = session_id
            ## retriever
            self.retriever = retriever
            ## laoding llm
            self.llm = self._load_llm()
            ## loading prompt
            self.contextualize_prompt = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            
            ## create chain which takes conversational history
            self.history_aware_retriever = create_history_aware_retriever(
                self.llm, self.retriever, self.contextualize_prompt
            )
            ## logging
            self.log.info("Created history-aware retriever", session_id = session_id)
            ## create a chain for passing list of documents to model
            self.qa_chain = create_stuff_documents_chain(self.llm, self.qa_prompt)
            
            ## create chain that retrieves documents and the passes them on
            self.rag_chain = create_retrieval_chain(self.history_aware_retriever, self.qa_chain)
            ## logging
            self.log.info("Created RAG chain", session_id=session_id)
            
            ## creating runnable that manages chat history for another runnable
            self.chain =RunnableWithMessageHistory(
                self.rag_chain,
                self._get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer"
            )
            ## logging
            self.log.info("Created RunnableWithMessageHistory",session_id=session_id)
            
            
        except Exception as e:
            self.log.error("Error initializing ConversationalRAG", error=str(e),session_id = session_id)
            raise DocumentPortalException("Failed to initialize ConversationalRAG", sys)
            
    def _load_llm(self):
        try:
            ## load llm
            llm = ModelLoader().load_llm()
            ## logging
            self.log.info("LLM loaded successfully", class_name = llm.__class__.__name__)
            return llm
        except Exception as e:
            self.log.error("Error loading LLM via ModelLoader", error=str(e))
            raise DocumentPortalException("Failed to load llm", sys)
        
    def _get_session_history(self, session_id:str):
        try:
            pass
        except Exception as e:
            self.log.error("Failed to access session history", error=str(e), session_id=session_id)
            raise DocumentPortalException("Failed to retrieve session history", sys)
        
    def load_retriever(self, index_path:str):
        try:
            ## loading embedding model
            embedding = ModelLoader().load_embedding_model()
            ## raising error if path is not directory
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")
            
            ## loading vector store
            vectorstore = FAISS.load_local(index_path, embedding)
            ## logging
            self.log.info("Loaded retriever from FAISS index", index_path=index_path)
            return vectorstore.as_retriever(search_type="similarity", search_kwargs = {"k":5})
            
        except Exception as e:
            self.log.error("Error loading retriever from FAISS", error=str(e))
            raise DocumentPortalException("Failed to load retriever from FAISS", sys)
        
    def invoke(self, user_input:str)->str:
        try:
            ## invoking the chain
            response = self.chain.invoke(
                {"input":user_input},
                config={"configurable":{"session_id":self.session_id}}
            )
            ## getting the response
            answer = response.get("answer", "No answer")
            ## if response is empty log warning
            if not answer:
                self.log.warning("Empty answer received", session_id = self.session_id)
            ## loggingg
            self.log.info("Chain invoked successfully", session_id=self.session_id, user_input = user_input, answer_preview = answer[:150])
            return answer
            
        except Exception as e:
            self.log.error("Error invoking Conversational RAG", error=str(e), session_id = self.session_id)
            raise DocumentPortalException("Failed to invoking Conversational RAG", sys)