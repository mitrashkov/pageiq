import json
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging() -> None:
    """Configure structured logging with file and console output"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Shared processors for all loggers
    shared_processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", key="timestamp"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _add_request_context,
    ]

    # Configure output format
    if settings.DEBUG:
        # Pretty printing for development
        shared_processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON logging for production
        shared_processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=shared_processors,
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    if settings.DEBUG:
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        console_formatter = JSONFormatter()

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler for production
    if not settings.DEBUG:
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "pageiq.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_formatter = JSONFormatter()
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set third-party loggers to WARNING to reduce noise
    for logger_name in ["urllib3", "httpx", "playwright", "asyncio", "redis"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Set alembic logger to INFO
    logging.getLogger("alembic").setLevel(logging.INFO)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in ["name", "msg", "args", "levelname", "levelno",
                              "pathname", "filename", "module", "exc_info",
                              "exc_text", "stack_info", "lineno", "funcName",
                              "created", "msecs", "relativeCreated", "thread",
                              "threadName", "processName", "process", "message"]:
                    log_data[key] = value

        return json.dumps(log_data, default=str)


def _add_request_context(logger: logging.Logger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add request context to log events"""
    # This will be enhanced when we have request context
    return event_dict


def get_request_logger(request_id: str = None) -> structlog.BoundLoggerBase:
    """Get a logger with request context"""
    if request_id:
        return structlog.get_logger().bind(request_id=request_id)
    return structlog.get_logger()