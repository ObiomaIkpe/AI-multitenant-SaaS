import enum

class DocumentStatus(str, enum.Enum):
    """
    Document processing status.
    
    Inherits from str to work with both:
    - SQLAlchemy (database enum type)
    - Pydantic (JSON serialization)
    """
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"