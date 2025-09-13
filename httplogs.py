"""
Utility module with functions for logging info on HTTP requests. It assumes the Requests library
is being used. Support for Httpx should be added.
"""

import logging
import json


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
