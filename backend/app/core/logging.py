import logging
import sys

import structlog

from app.core.config import settings

_configured = False

def configure_logging():
    """
    Structured JSON logs with level/timestamp/exception info, so both the
    FastAPI process and the MCP server (stdio or HTTP) produce greppable,
    machine-parseable log lines carrying whatever context fields a call
    site attaches (e.g. request_id, tool_name, duration_ms).

    Safe to call multiple times - only configures once.
    """

    global _configured
    if _configured:
        return
    

    level = getattr(logging, settings.log_level.upper(),logging.INFO)

    logging.basicConfig(format = "%(message)s",stream = sys.stderr,level = level)

    structlog.configure(
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TImestamper(fmt = "iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(sort_keys = True),
            structlog.processors.StackInfoRenderer(),
        ],
        wrapper_class = structlog.make_filtering_bound_logger(level),
        context_class = dict,
        logger_factory = structlog.PrintLoggerFactory(file = sys.stderr),
        cache_logger_on_first_use = True,
    )

    _configured = True

def get_logger(name: str = "ragdocs"):
    configure_logging()
    return structlog.get_logger(name)


