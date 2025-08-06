import os
from utils.model_loader import ModelLoader
from exception.custom_exception import DocumentPortalException
from logger.custom_logger import CustomLogger
from model.models import *

from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser


class DocumentAnalyzer:
    """
    Analyze document using a pre-trained model.
    Automatically logs all action and supports session-based organization.
    """
    
    def __init__(self):
        pass
    
    def analyze_metdata(self):
        pass