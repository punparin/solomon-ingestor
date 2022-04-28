from Ingestor import Ingestor
from Logger import Logger


if __name__ == "__main__":
    logger = Logger()
    ingestor = Ingestor(logger)

    ingestor.process()
