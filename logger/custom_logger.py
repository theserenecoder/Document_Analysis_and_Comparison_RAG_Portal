import logging
import os
from datetime import datetime
class CustomLogger:
    
    def __init__(self, log_dir = 'logs'):
        self.logs_dir = os.path.join(os.getcwd(),log_dir)
        ## creating the directory, if exists will use that
        os.makedirs(self.logs_dir, exist_ok=True)
        
        ## Create timestamped log filename
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S.log')}"
        log_file_path = os.path.join(self.logs_dir, log_file)
        
        ## Configure Logging
        logging.basicConfig(
            filename=log_file_path,
            format="[ %(asctime)s ] %(levelname)s %(name)s (line:%(lineno)d) - %(message)s",
            level=logging.INFO,
        )
    
    def get_logger(self, name=__file__):
        return logging.getLogger(os.path.basename(name))
    
if __name__ == '__main__':
    logger = CustomLogger()
    logger  =logger.get_logger(__file__)
    logger.info('This is test info')