"""
Module for setting up application logging.
"""

import logging
import os.path
import json
import atexit


logger = logging.getLogger(__name__)


def get_handler_by_name(name: str):
    """This can be removed in Python 3.12 since there we have logging.getHandlerByName."""
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            if handler.name == name:
                return handler
    # also check root logger
    for handler in logging.getLogger().handlers:
        if handler.name == name:
            return handler
    return None


def setup_logging(config_filepath):
    """Set up logging. If no logging config file is found, set up default logging."""
    if os.path.exists(config_filepath):
        with open(config_filepath) as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        queue_handler = get_handler_by_name("queue_handler")
        if queue_handler is not None:
            queue_handler.listener.start()
            atexit.register(queue_handler.listener.stop)
    else:
        logger.setLevel("DEBUG")
        logger.warning(f"Configuration file '{config_filepath}' for logging not found. "
                       "Using default logging settings.")


def log_request(logger,
                r,
                message: str = "HTTP request",
                request_headers_to_strip_away: list[str] = None):
    """Log `message` about the HTTP request `r` using the provided `logger` and add some extra data
       about the request and response. The extra data is extensive if the logging level is DEBUG,
       otherwise limited if the logging level is INFO. `request_headers_to_strip_away` lists
       request headers that should be stripped away and not logged, e.g. API keys."""
    extra = {"Request method": r.request.method,
             "Request URL": r.url,
             "Response status": f"{r.status_code} ({r.reason})"}
    if logger.isEnabledFor(logging.DEBUG):
        # Remove sensitive HTTP headers
        d = dict(r.request.headers)
        for header in request_headers_to_strip_away:
            del d[header]
        # Make sure the request body is logged as JSON
        if r.request.body:
            body = json.loads(r.request.body)
        else:
            body = None
        debug_extra = {"Request headers": d,
                       "Request URL": r.url,
                       "Request body": body,
                       "Response status": f"{r.status_code} ({r.reason})",
                       "Response headers": dict(r.headers),
                       "Response body": r.json()}
        extra.update(debug_extra)
        logger.debug(message,
                     extra=extra)
    else:
        logger.info(message,
                    extra=extra)
