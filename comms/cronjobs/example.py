import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.INFO)


def run():
    logging.info("Hello world!")
    logging.warning("This is a warning - don't do it again!")
    logging.error("Resources overloaded, shutting down.")
