import logging

logging.basicConfig(
    format='%(asctime)-15s - %(module)s - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO
)
logger = logging.getLogger('evoc')
logger.setLevel(logging.INFO)
