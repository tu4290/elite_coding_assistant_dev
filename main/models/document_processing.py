from pydantic import BaseModel, FilePath, HttpUrl, field_validator, Field
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import datetime
import uuid

class DocumentType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "md"
    TXT = "txt"
    HTML = "html"
    PYTHON = "py" # Added for code files
    JSON = "json"
    YAML = "yaml"
    UNKNOWN = "unknown"

class DocumentSource(BaseModel):
    file_path: Optional[FilePath] = None
    url: Optional[HttpUrl] = None
    content_bytes: Optional[bytes] = None
    file_name: Optional[str] = None
    document_type: Optional[DocumentType] = None # Allow manual specification

    @field_validator('file_name', always=True)
    def check_source_provided(cls, v, values):
        data = values.data # Access all fields via .data
        if not data.get('file_path') and not data.get('url') and not data.get('content_bytes'):
            raise ValueError("Either file_path, url, or content_bytes must be provided.")
        if data.get('content_bytes') and not v:
            raise ValueError("file_name must be provided if content_bytes is used.")
        return v

class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    creation_date: Optional[datetime.datetime] = None
    modification_date: Optional[datetime.datetime] = None
    keywords: List[str] = Field(default_factory=list)
    source_filename: Optional[str] = None
    detected_language: Optional[str] = None
    custom_properties: Dict[str, Any] = Field(default_factory=dict)
    page_count: Optional[int] = None # For PDFs
    word_count: Optional[int] = None

class DocumentContent(BaseModel):
    raw_text: str
    metadata: DocumentMetadata
    document_type: DocumentType

class ContentChunk(BaseModel):
    text: str
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str # Reference to the parent document's ID in Supabase
    order: int # Sequence of the chunk within the document
    metadata: Dict[str, Any] = Field(default_factory=dict) # e.g., page number, section header

class EmbeddedChunk(ContentChunk):
    embedding: List[float]
    embedding_model_name: str

class QualityScore(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    clarity: float = Field(ge=0.0, le=1.0)
    relevance_score: Optional[float] = Field(default=None, ge=0.0, le=1.0) # e.g. to filename or query
    potential_issues: List[str] = Field(default_factory=list)

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success" # e.g. content extracted, but embedding failed
    FAILURE = "failure"

class ProcessingResult(BaseModel):
    document_id: str # Unique ID for the processed document (from Supabase processed_documents table)
    source_display_name: str # filename or URL
    extracted_content: Optional[DocumentContent] = None
    chunks: Optional[List[ContentChunk]] = None
    embedded_chunks: Optional[List[EmbeddedChunk]] = None
    quality_score: Optional[QualityScore] = None
    processing_time_seconds: float
    status: ProcessingStatus
    error_message: Optional[str] = None
    chunk_count: Optional[int] = 0
    embedded_chunk_count: Optional[int] = 0

# For Supabase 'processed_documents' table
class ProcessedDocumentEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_file_path: Optional[str] = None
    source_url: Optional[str] = None
    source_file_name: Optional[str] = None # Original filename
    document_type: DocumentType
    status: ProcessingStatus
    processing_started_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    processing_ended_at: Optional[datetime.datetime] = None
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None # Store DocumentMetadata here
    quality_score: Optional[Dict[str, Any]] = None # Store QualityScore here
    chunk_count: int = 0
    embedded_chunk_count: int = 0

# For Supabase 'knowledge_base' table (representing a single chunk)
class KnowledgeBaseEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())) # Chunk's own UUID
    processed_document_id: str # FK to processed_documents table
    document_source_name: str # e.g. original filename or URL of the document
    chunk_order: int
    content: str # Text of the chunk
    embedding: List[float]
    embedding_model_name: str
    metadata: Dict[str, Any] = Field(default_factory=dict) # Chunk-specific metadata (page, section)
    document_metadata: Dict[str, Any] = Field(default_factory=dict) # Metadata of the parent document
    document_quality_score: float # Overall quality of the parent document
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    @field_validator('updated_at', always=True)
    def set_updated_at(cls, v):
        return datetime.datetime.utcnow()
