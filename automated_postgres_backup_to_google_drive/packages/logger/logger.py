import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_app_logger(logger_name, log_file_path=None):

    # Create a logger
    logger = logging.getLogger(logger_name)

    # Set the level of logging
    logger.setLevel(logging.DEBUG)

    # Set the format of the log message
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set the log handler
    log_handler = logging.StreamHandler(sys.stdout)

    # Set the log message format we've created to the log handler
    log_handler.setFormatter(formatter)

    # Clear any previous handlers and add a new handler
    logger.handlers.clear()
    logger.addHandler(log_handler)

    # Check if the function received a file name; to insert the logs inside it
    if log_file_path:

        # Set a FileHandler write the logs inside the file
        file_handler = RotatingFileHandler(
            filename=log_file_path, mode='a', maxBytes=5*1024*1024,
            backupCount=100, encoding=None, delay=False
        )

        # Set the format of the FileHandler
        file_handler.setFormatter(formatter)

        # Add the filehandler
        logger.addHandler(file_handler)


    # Return the logger
    return logger


def create_log_file(app_name, project_abs_path):

    # Create logs folder if not exists
    logs_folder_path = os.path.join(project_abs_path, 'logs')
    if not os.path.exists(logs_folder_path):
        os.makedirs(logs_folder_path)

    # Get current timestamp
    current_timestamp = str(datetime.now().strftime("%Y-%m-%d__%H-%M-%S"))

    # Logs file name
    logs_file_name = app_name + "__" + current_timestamp + ".log"

    # Logs file path
    logs_file_path = os.path.join(project_abs_path, 'logs', logs_file_name)

    # Create the logs file if not exists
    if not os.path.exists(logs_file_path):
        open(logs_file_path, 'w').close()

    return logs_file_path


if __name__ == '__main__':

    # Create log file
    logs_file_ = create_log_file(
        app_name='test', project_abs_path='/'
    )

    # Initiate logger
    logger = setup_app_logger(logger_name='test', log_file_path=logs_file_)

    logger.info('test')
