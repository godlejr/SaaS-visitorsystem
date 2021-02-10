import logging
import sys

from flask import request

from visitorsystem.models import Ssctenant


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
    logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
    # logging.getLogger('sqlalchemy.dialects').setLevel(logging.DEBUG)
    # logging.getLogger('sqlalchemy.orm').setLevel(logging.DEBUG)

    def __init__(self):
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        stream_hander = logging.StreamHandler(sys.stderr)
        formmater = logging.Formatter('[%(asctime)s][%(levelname)s][%(module)s][%(name)s]%(message)s')
        stream_hander.setFormatter(formmater)
        logger.addHandler(stream_hander)
