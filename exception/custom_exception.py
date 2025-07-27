import sys
import traceback
from logger.custom_logger import CustomLogger

logger = CustomLogger().get_logger(__file__)

class DocumentPortalException(Exception):
    '''Custom Exception for document portal'''
    
    def __init__(self, error_messge, error_details:sys):
        ## .exe_info() provides the complete execution detail
        _,_,exc_tb = error_details.exc_info()
        ## from our exception traceback we will capture the line number and file number
        self.file_name = exc_tb.tb_frame.f_code.co_filename
        self.line_no = exc_tb.tb_lineno
        self.error_message = str(error_messge)
        ## We will also take the complete traceback detail
        self.traceback_str = ''.join(traceback.format_exception(*error_details.exc_info()))
        
    def __str__(self):
        return f"""
        Error in [{self.file_name}] at line no [{self.line_no}]
        Message : {self.error_message}
        Traceback:
        {self.traceback_str}
        """
        
if __name__ == "__main__":
    try:
        # Simulate an error
        a = 1 / 0
        print(a)
    except Exception as e:
        app_exc=DocumentPortalException(e,sys)
        logger.error(app_exc)
        raise app_exc