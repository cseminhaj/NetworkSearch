import logging.config

from pkg_resources import resource_stream

import utils

class LoggerFactory(object):
    DEFAULT_LOG_CONFIG = "logging.cfg"

    @staticmethod
    def create_logger(instance):
        if utils.isstr(instance):
            return logging.getLogger(instance)
        else:
            return logging.getLogger("%s.%s" % (instance.__module__, instance.__class__.__name__))

    @staticmethod
    def init(config_file=None):
        if config_file is None:
            config = resource_stream(__name__, LoggerFactory.DEFAULT_LOG_CONFIG)
        else:
            config = resource_stream(__name__, config_file)
