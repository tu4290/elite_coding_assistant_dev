import asyncio
import datetime
import hashlib
import logging
import mimetypes
import os
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple

import httpx
# Conditional imports for parsers to avoid hard dependencies if a type is not used
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
try:
    import docx
except ImportError:
    docx = None
try:
    import markdown as md_parser
except ImportError:
    md_parser = None
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
try:
    import magic
except ImportError:
    magic = None

from langchain.text_splitter import RecursiveCharacterTextSplitter

from main.models.document_processing import (
    DocumentSource, ProcessingResult, DocumentContent, ContentChunk,
    EmbeddedChunk, QualityScore, DocumentType, DocumentMetadata,
    ProcessingStatus, ProcessedDocumentEntry, KnowledgeBaseEntry
)
# Assuming SupabaseLearningClient and ModelManager are importable
# from main.supabase_learning_client import SupabaseLearningClient, SupabaseClient  # Actual client might be SupabaseClient
# from main.model_manager import ModelManager

# Placeholder for actual Supabase and ModelManager clients
# These would be properly imported in the actual project structure
class SupabaseLearningClient:
    async def upsert_processed_document(self, doc_entry: ProcessedDocumentEntry) -> Dict[str, Any]:
        logging.info(f"Supabase: Upserting processed document {doc_entry.id}")
        return {"id": doc_entry.id, "status": "success"} # Mock response

    async def upsert_knowledge_base_entries(self, entries: List[KnowledgeBaseEntry]) -> Dict[str, Any]:
        logging.info(f"Supabase: Upserting {len(entries)} knowledge base entries.")
        return {"count": len(entries), "status": "success"} # Mock response

class ModelManager:
    async def get_embeddings(self, texts: List[str], model_name: str = "default_embedding_model") -> List[List[float]]:
        logging.info(f"ModelManager: Generating embeddings for {len(texts)} texts using {model_name}.")
        # Mock embeddings (e.g., 1536 dimensions for OpenAI Ada)
        return [[0.01 * i for i in range(1536)] for _ in texts]


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIngestionSystem:
    def __init__(self, supabase_client: SupabaseLearningClient, model_manager: ModelManager, text_splitter_config: Optional[Dict[str, Any]] = None):
        self.supabase_client = supabase_client
        self.model_manager = model_manager

        default_splitter_config = {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "length_function": len,
        }
        current_splitter_config = {**default_splitter_config, **(text_splitter_config or {})}
        self.text_splitter = RecursiveCharacterTextSplitter(**current_splitter_config)
        logger.info(f"DocumentIngestionSystem initialized with text_splitter config: {current_splitter_config}")

    def _get_file_extension(self, filename: str) -> Optional[str]:
        return os.path.splitext(filename)[1].lstrip('.').lower() if filename else None

    def _detect_document_type(self, source: DocumentSource, content_bytes: Optional[bytes] = None) -> DocumentType:
        if source.document_type:
            return source.document_type

        filename = source.file_name or (source.file_path.name if source.file_path else None)
        ext = self._get_file_extension(filename)

        if ext:
            try:
                return DocumentType(ext)
            except ValueError:
                logger.warning(f"Unknown extension: {ext} for file {filename}. Trying magic.")

        if content_bytes and magic:
            mime_type = magic.from_buffer(content_bytes, mime=True)
            logger.info(f"Detected MIME type: {mime_type} for {filename or 'bytes_content'}")
            if mime_type == "application/pdf": return DocumentType.PDF
            if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document": return DocumentType.DOCX
            if mime_type == "text/markdown": return DocumentType.MARKDOWN
            if mime_type == "text/html": return DocumentType.HTML
            if mime_type == "text/plain": return DocumentType.TXT
            if mime_type == "application/json": return DocumentType.JSON
            if mime_type in ["application/x-yaml", "text/yaml"]: return DocumentType.YAML
            if mime_type == "text/x-python": return DocumentType.PYTHON

        # Fallback if extension is missing or magic is not available/conclusive
        if filename: # Try common code extensions if filename is available
            if ext == "py": return DocumentType.PYTHON
            if ext == "json": return DocumentType.JSON
            if ext == "yaml" or ext == "yml": return DocumentType.YAML
            if ext == "md": return DocumentType.MARKDOWN
            if ext == "txt": return DocumentType.TXT
            if ext == "html" or ext == "htm": return DocumentType.HTML

        logger.warning(f"Could not determine document type for {filename or 'bytes_content'}. Defaulting to UNKNOWN.")
        return DocumentType.UNKNOWN

    def _extract_metadata_stub(self, file_path: Optional[str], doc_type: DocumentType) -> DocumentMetadata:
        # Placeholder for actual metadata extraction logic
        filename = os.path.basename(file_path) if file_path else "unknown_file"
        return DocumentMetadata(
            title=filename,
            source_filename=filename,
            creation_date=datetime.datetime.utcnow(),
            modification_date=datetime.datetime.utcnow()
        )

    def _parse_pdf(self, content_bytes: bytes) -> str:
        if not PyPDF2:
            raise ImportError("PyPDF2 is not installed. Please install it to process PDF files.")
        try:
            from io import BytesIO
            reader = PyPDF2.PdfReader(BytesIO(content_bytes))
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() or ""
            return text
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return ""

    def _parse_docx(self, content_bytes: bytes) -> str:
        if not docx:
            raise ImportError("python-docx is not installed. Please install it to process DOCX files.")
        try:
            from io import BytesIO
            document = docx.Document(BytesIO(content_bytes))
            return "\n".join([para.text for para in document.paragraphs])
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            return ""

    def _parse_markdown(self, text_content: str) -> str:
        if not md_parser:
            raise ImportError("Markdown is not installed. Please install it to process Markdown files.")
        try:
            # Basic conversion to text, consider more sophisticated HTML to text if needed
            html = md_parser.markdown(text_content)
            # Simple text extraction from HTML, could be improved
            soup = BeautifulSoup(html, "html.parser") if BeautifulSoup else None
            return soup.get_text() if soup else html
        except Exception as e:
            logger.error(f"Error parsing Markdown: {e}")
            return text_content # Fallback to original text

    def _parse_html(self, text_content: str) -> str:
        if not BeautifulSoup:
            raise ImportError("BeautifulSoup4 is not installed. Please install it to process HTML files.")
        try:
            soup = BeautifulSoup(text_content, "html.parser")
            # Remove script and style tags
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return ""

    async def _fetch_url_content(self, url: HttpUrl) -> Tuple[Optional[bytes], Optional[str]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(str(url), follow_redirects=True, timeout=30.0)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").split(";")[0]
                return response.content, content_type
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching {url}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Request error fetching {url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
        return None, None


    async def extract_content_from_source(self, source: DocumentSource) -> Optional[DocumentContent]:
        content_bytes: Optional[bytes] = None
        file_name = source.file_name

        if source.file_path:
            file_name = file_name or source.file_path.name
            try:
                with open(source.file_path, "rb") as f:
                    content_bytes = f.read()
            except Exception as e:
                logger.error(f"Error reading file {source.file_path}: {e}")
                return None
        elif source.url:
            file_name = file_name or str(source.url).split('/')[-1] or "web_document"
            content_bytes, _ = await self._fetch_url_content(source.url)
            if not content_bytes:
                return None
        elif source.content_bytes:
            content_bytes = source.content_bytes
            if not file_name: # Should be caught by Pydantic validator, but double check
                 logger.error("File name is required when providing content_bytes.")
                 return None
        else:
            logger.error("No valid document source provided.")
            return None

        doc_type = self._detect_document_type(source, content_bytes)
        raw_text = ""

        if doc_type == DocumentType.PDF:
            raw_text = self._parse_pdf(content_bytes)
        elif doc_type == DocumentType.DOCX:
            raw_text = self._parse_docx(content_bytes)
        elif doc_type == DocumentType.MARKDOWN:
            raw_text = self._parse_markdown(content_bytes.decode('utf-8', errors='ignore'))
        elif doc_type == DocumentType.HTML:
            raw_text = self._parse_html(content_bytes.decode('utf-8', errors='ignore'))
        elif doc_type in [DocumentType.TXT, DocumentType.PYTHON, DocumentType.JSON, DocumentType.YAML]:
            raw_text = content_bytes.decode('utf-8', errors='ignore')
        else: # UNKNOWN or unhandled
            logger.warning(f"No specific parser for {doc_type} of file {file_name}. Trying plain text.")
            try:
                raw_text = content_bytes.decode('utf-8', errors='ignore')
            except Exception as e:
                logger.error(f"Could not decode content as UTF-8 for {file_name}: {e}")
                return None

        if not raw_text.strip():
            logger.warning(f"No text extracted from {file_name} (type: {doc_type}).")
            # Optionally, you might want to return None or an empty DocumentContent
            # For now, let's proceed, quality validation might catch this.

        # Placeholder for actual metadata extraction
        metadata = self._extract_metadata_stub(str(source.file_path) if source.file_path else file_name, doc_type)
        metadata.source_filename = file_name
        metadata.word_count = len(raw_text.split())

        return DocumentContent(raw_text=raw_text, metadata=metadata, document_type=doc_type)

    def chunk_content(self, text: str, document_id: str) -> List[ContentChunk]:
        if not text.strip():
            return []
        split_texts = self.text_splitter.split_text(text)
        return [
            ContentChunk(text=chunk_text, document_id=document_id, order=i)
            for i, chunk_text in enumerate(split_texts)
            if chunk_text.strip() # Ensure chunks are not just whitespace
        ]

    async def generate_embeddings(self, chunks: List[ContentChunk], embedding_model_name: str = "text-embedding-ada-002") -> List[EmbeddedChunk]:
        if not chunks:
            return []

        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = await self.model_manager.get_embeddings(chunk_texts, model_name=embedding_model_name)

        embedded_chunks = []
        for i, chunk in enumerate(chunks):
            embedded_chunks.append(
                EmbeddedChunk(
                    **chunk.model_dump(),
                    embedding=embeddings[i],
                    embedding_model_name=embedding_model_name
                )
            )
        return embedded_chunks

    def validate_content_quality(self, content: Optional[DocumentContent], chunks: Optional[List[ContentChunk]]) -> QualityScore:
        # Basic quality heuristics
        issues = []
        if not content or not content.raw_text.strip():
            issues.append("No content extracted or content is empty.")
            return QualityScore(overall_score=0.0, completeness=0.0, clarity=0.0, potential_issues=issues)

        completeness = 1.0 if len(content.raw_text) > 100 else len(content.raw_text) / 100.0
        clarity = 1.0 # Placeholder, could use readability scores or other metrics

        if not chunks or len(chunks) == 0 :
            if content.raw_text.strip(): # If there was content but no chunks, it's an issue
                 issues.append("Content could not be chunked effectively.")
                 completeness = min(completeness, 0.5) # Penalize completeness

        # More checks can be added: language detection confidence, ratio of non-alphanumeric, etc.
        overall = (completeness + clarity) / 2
        if issues:
            overall = max(0.0, overall - 0.2 * len(issues)) # Penalize for issues

        return QualityScore(
            overall_score=min(1.0, max(0.0, overall)),
            completeness=min(1.0, max(0.0, completeness)),
            clarity=min(1.0, max(0.0, clarity)),
            potential_issues=issues
        )

    async def store_in_knowledge_base(self, processed_doc_entry: ProcessedDocumentEntry, embedded_chunks: List[EmbeddedChunk]) -> None:
        if not embedded_chunks:
            logger.info(f"No embedded chunks to store for document {processed_doc_entry.id}")
            return

        kb_entries = []
        for chunk in embedded_chunks:
            entry = KnowledgeBaseEntry(
                processed_document_id=processed_doc_entry.id,
                document_source_name=processed_doc_entry.source_file_name or processed_doc_entry.source_url or "unknown_source",
                chunk_order=chunk.order,
                content=chunk.text,
                embedding=chunk.embedding,
                embedding_model_name=chunk.embedding_model_name,
                metadata=chunk.metadata, # Chunk specific metadata (page, section, etc.)
                document_metadata=processed_doc_entry.metadata or {},
                document_quality_score=processed_doc_entry.quality_score.get("overall_score", 0.0) if processed_doc_entry.quality_score else 0.0,
            )
            kb_entries.append(entry)

        await self.supabase_client.upsert_knowledge_base_entries(kb_entries)
        logger.info(f"Stored {len(kb_entries)} chunks for document {processed_doc_entry.id} in knowledge base.")


    async def process_document(self, source: DocumentSource) -> ProcessingResult:
        start_time = time.time()

        source_display_name = source.file_name or (source.file_path.name if source.file_path else str(source.url))
        doc_type_for_entry = self._detect_document_type(source) # Detect once for ProcessedDocumentEntry

        processed_doc_entry = ProcessedDocumentEntry(
            source_file_path=str(source.file_path) if source.file_path else None,
            source_url=str(source.url) if source.url else None,
            source_file_name=source_display_name,
            document_type=doc_type_for_entry,
            status=ProcessingStatus.PENDING
        )

        try:
            logger.info(f"Starting processing for: {source_display_name}")

            document_content = await self.extract_content_from_source(source)

            if not document_content or not document_content.raw_text.strip():
                error_msg = f"Failed to extract text content from {source_display_name}."
                logger.error(error_msg)
                processed_doc_entry.status = ProcessingStatus.FAILURE
                processed_doc_entry.error_message = error_msg
                quality_score_obj = self.validate_content_quality(document_content, None) # Get a score even on failure
                processed_doc_entry.quality_score = quality_score_obj.model_dump()
                return ProcessingResult(
                    document_id=processed_doc_entry.id,
                    source_display_name=source_display_name,
                    status=ProcessingStatus.FAILURE,
                    error_message=error_msg,
                    processing_time_seconds=time.time() - start_time,
                    quality_score=quality_score_obj
                )

            processed_doc_entry.metadata = document_content.metadata.model_dump()

            content_chunks = self.chunk_content(document_content.raw_text, processed_doc_entry.id)
            processed_doc_entry.chunk_count = len(content_chunks)

            if not content_chunks:
                logger.warning(f"No content chunks generated for {source_display_name}. Document might be too small or empty after cleaning.")

            embedded_chunks = await self.generate_embeddings(content_chunks) # Default model used here
            processed_doc_entry.embedded_chunk_count = len(embedded_chunks)

            quality_score_obj = self.validate_content_quality(document_content, content_chunks)
            processed_doc_entry.quality_score = quality_score_obj.model_dump()

            if quality_score_obj.overall_score < 0.3: # Configurable threshold
                 logger.warning(f"Document {source_display_name} has low quality score ({quality_score_obj.overall_score}). Potential issues: {quality_score_obj.potential_issues}")
                 # Decide if to proceed with storage or mark as failure based on quality

            await self.store_in_knowledge_base(processed_doc_entry, embedded_chunks)

            processed_doc_entry.status = ProcessingStatus.SUCCESS
            processing_time = time.time() - start_time
            processed_doc_entry.processing_time_seconds = processing_time
            processed_doc_entry.processing_ended_at = datetime.datetime.utcnow()

            await self.supabase_client.upsert_processed_document(processed_doc_entry)

            return ProcessingResult(
                document_id=processed_doc_entry.id,
                source_display_name=source_display_name,
                extracted_content=document_content,
                chunks=content_chunks,
                embedded_chunks=embedded_chunks,
                quality_score=quality_score_obj,
                processing_time_seconds=processing_time,
                status=ProcessingStatus.SUCCESS,
                chunk_count=len(content_chunks),
                embedded_chunk_count=len(embedded_chunks)
            )

        except Exception as e:
            logger.exception(f"Error processing document {source_display_name}: {e}")
            processing_time = time.time() - start_time
            processed_doc_entry.status = ProcessingStatus.FAILURE
            processed_doc_entry.error_message = str(e)
            processed_doc_entry.processing_time_seconds = processing_time
            processed_doc_entry.processing_ended_at = datetime.datetime.utcnow()

            # Try to update Supabase with failure status
            try:
                await self.supabase_client.upsert_processed_document(processed_doc_entry)
            except Exception as db_e:
                logger.error(f"Failed to update Supabase with error status for {processed_doc_entry.id}: {db_e}")

            return ProcessingResult(
                document_id=processed_doc_entry.id,
                source_display_name=source_display_name,
                status=ProcessingStatus.FAILURE,
                error_message=str(e),
                processing_time_seconds=processing_time
            )

    async def process_batch(self, sources: List[DocumentSource]) -> List[ProcessingResult]:
        results = await asyncio.gather(
            *[self.process_document(source) for source in sources]
        )
        return results

# Example Usage (for testing purposes, not part of the class)
async def main_test():
    # Mock Supabase and ModelManager clients
    supabase_client = SupabaseLearningClient()
    model_manager = ModelManager()

    ingestion_system = DocumentIngestionSystem(supabase_client, model_manager)

    # Create a dummy text file for testing
    dummy_file_path = "dummy_document.txt"
    with open(dummy_file_path, "w") as f:
        f.write("This is a test document.\nIt has multiple lines.\nAnd some simple content for chunking and embedding.")

    source1 = DocumentSource(file_path=dummy_file_path, file_name="dummy_document.txt")

    # Test with a non-existent file
    source2 = DocumentSource(file_path="non_existent_file.txt", file_name="non_existent_file.txt")

    # Test with bytes
    byte_content = b"This is a byte string document content for testing."
    source3 = DocumentSource(content_bytes=byte_content, file_name="bytes_doc.txt")

    results = await ingestion_system.process_batch([source1, source2, source3])

    for result in results:
        logger.info(f"Result for {result.source_display_name}: Status - {result.status}, Chunks - {result.chunk_count}")
        if result.error_message:
            logger.error(f"Error: {result.error_message}")
        if result.quality_score:
            logger.info(f"Quality Score: {result.quality_score.overall_score}")

    # Clean up dummy file
    if os.path.exists(dummy_file_path):
        os.remove(dummy_file_path)

if __name__ == "__main__":
    # This is for local testing of the script if run directly.
    # Ensure you have an event loop running if you call this directly.
    # For example, in a Jupyter notebook or by wrapping main_test() with asyncio.run()
    # asyncio.run(main_test())
    pass
