import logging, json_logging, sys

def log(t):
    if t == "S3":
        log_ = logging.getLogger('S3')
    elif t == "Redis":
        log_ = logging.getLogger('Redis')
    elif t == "Transaction":
        log_ = logging.getLogger('Transaction')

    return log_


class loggerSet():
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    # logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
    # logging.getLogger('sqlalchemy.dialects').setLevel(logging.DEBUG)
    # logging.getLogger('sqlalchemy.orm').setLevel(logging.DEBUG)

    def __init__(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        stream_hander = logging.StreamHandler(sys.stderr)
        stream_hander.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s] - %(module)s/%(message)s'))
        logger.addHandler(stream_hander)