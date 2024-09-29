import logging, sys

LOGGER_NAME = "logging"

def setup_applevel_logger(logger_name= LOGGER_NAME, is_debug = True, file_name = None):
    logger = logging.getLogger(logger_name)
    logger.setLevel("DEBUG")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - Logger:%(levelname)s - %(message)s"
    )

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(sh)

    if file_name:
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

def get_logger(module_name):
    return logging.getLogger(LOGGER_NAME).getChild(module_name)