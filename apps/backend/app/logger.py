import json
import logging
import sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    """
    Format standard logger records into structured JSON single-line strings.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "filename": record.filename,
            "line_number": record.lineno
        }
        
        # Add stack trace details if exception occurred
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging(default_level: int = logging.INFO) -> None:
    """
    Configures the root logging stream to output JSON records.
    """
    root = logging.getLogger()
    root.setLevel(default_level)
    
    # Avoid duplicate handlers
    if not any(isinstance(h, logging.StreamHandler) and h.stream == sys.stdout for h in root.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        root.addHandler(handler)
        
        # Disable default handlers to avoid duplicates
        for h in root.handlers[:-1]:
            root.removeHandler(h)
            
    # Quiet verbose library loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
