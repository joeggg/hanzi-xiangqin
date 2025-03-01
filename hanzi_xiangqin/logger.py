import logging


def set_up_logging() -> None:
    logger = logging.getLogger("")
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s-[%(name)s]-[%(levelname)s]: %(message)s")

    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
