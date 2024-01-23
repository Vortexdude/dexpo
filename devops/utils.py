import logging
 

FORMAT = '[%(levelname)s] - %(asctime)s - %(name)s - %(message)s'
# Create and configure logger

logging.basicConfig(
    filename="file.log",
    format=FORMAT,
    filemode="w"
)

# Creating an object
logger = logging.getLogger("EC2")
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.INFO)
