import asyncio
import datetime
import hashlib
import logging
import mimetypes
import os
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

import httpx

# Conditional imports for parsers
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
    logging.warning("PyPDF2 not found. PDF parsing will not be available.")
try:
    import docx
except ImportError:
    docx = None
    logging.warning("python-docx not found. DOCX parsing will not be available.")
try:
    import markdown as md_parser
except ImportError:
    md_parser = None
    logging.warning("markdown not found. Markdown parsing will be basic.")
try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
    logging.warning("BeautifulSoup4 not found. HTML parsing will be basic.")
try:
    import magic
except ImportError:
    magic = None
    logging.warning("python-magic not found. File type detection will rely on extensions only.")

from langchain.text_splitter import RecursiveCharacterTextSplitter

from main.models.document_processing import (
    DocumentSource, ProcessingResult, DocumentContent, ContentChunk,
    EmbeddedChunk, QualityScore, DocumentType, DocumentMetadata,
    ProcessingStatus, ProcessedDocumentEntry, KnowledgeBaseEntry
)
# These will be the actual classes from your project:
from main.supabase_learning_client import SupabaseLearningClient
from main.model_manager import ModelManager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentIngestionSystem:
    def __init__(self, supabase_client: SupabaseLearningClient, model_manager: ModelManager, text_splitter_config: Optional[Dict[str, Any]] = None):
        self.supabase_client = supabase_client
        self.model_manager = model_manager

        default_splitter_config = {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "length_function": len,
            "add_start_index": True, # Useful for referencing source
        }
        current_splitter_config = {**default_splitter_config, **(text_splitter_config or {})}
        self.text_splitter = RecursiveCharacterTextSplitter(**current_splitter_config)
        logger.info(f"DocumentIngestionSystem initialized with text_splitter config: {current_splitter_config}")

    def _get_file_extension(self, filename: Optional[str]) -> Optional[str]:
        return os.path.splitext(filename)[1].lstrip('.').lower() if filename else None

    def _detect_document_type(self, source: DocumentSource, content_bytes: Optional[bytes] = None) -> DocumentType:
        if source.document_type: # Manual override
            return source.document_type

        filename = source.file_name or (Path(source.file_path).name if source.file_path else None)

        # 1. Try extension first
        ext = self._get_file_extension(filename)
        if ext:
            try:
                # Direct mapping for common types
                if ext == "pdf": return DocumentType.PDF
                if ext == "docx": return DocumentType.DOCX
                if ext == "md": return DocumentType.MARKDOWN
                if ext == "txt": return DocumentType.TXT
                if ext == "html" or ext == "htm": return DocumentType.HTML
                if ext == "py": return DocumentType.PYTHON
                if ext == "json": return DocumentType.JSON
                if ext == "yaml" or ext == "yml": return DocumentType.YAML
                # For other extensions, Pydantic's DocumentType(ext) might work if defined
                dt = DocumentType(ext)
                logger.info(f"Detected type by extension '{ext}' as {dt} for {filename}")
                return dt
            except ValueError:
                logger.info(f"Extension '{ext}' for {filename} not a direct DocumentType. Trying MIME.")

        # 2. Try MIME type using python-magic if available and content_bytes provided
        if content_bytes and magic:
            try:
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
            except Exception as e:
                logger.warning(f"python-magic failed for {filename or 'bytes_content'}: {e}")

        logger.warning(f"Could not determine document type for {filename or 'bytes_content'}. Defaulting to UNKNOWN.")
        return DocumentType.UNKNOWN

    def _extract_metadata(self, source: DocumentSource, doc_type: DocumentType, content_bytes: Optional[bytes]) -> DocumentMetadata:
        filename = source.file_name or (Path(source.file_path).name if source.file_path else str(source.url).split('/')[-1] if source.url else "unknown_file")

        title = Path(filename).stem.replace("_", " ").replace("-", " ")
        creation_time = datetime.datetime.utcnow()
        mod_time = datetime.datetime.utcnow()

        if source.file_path and os.path.exists(source.file_path):
            try:
                stat = os.stat(source.file_path)
                creation_time = datetime.datetime.fromtimestamp(stat.st_ctime)
                mod_time = datetime.datetime.fromtimestamp(stat.st_mtime)
            except Exception: # Fallback if stat fails
                pass

        # Add more specific metadata extraction based on doc_type if library supports it
        # e.g., for PDFs: author, page_count from PyPDF2
        # e.g., for DOCX: author, core_properties from python-docx

        return DocumentMetadata(
            title=title,
            source_filename=filename,
            creation_date=creation_time,
            modification_date=mod_time,
            # detected_language: Placeholder, use langdetect or similar if needed
        )

    def _parse_pdf(self, content_bytes: bytes, source_name: str) -> str:
        if not PyPDF2:
            logger.error("PyPDF2 is not installed. Cannot parse PDF files.")
            raise ImportError("PyPDF2 is not installed. Please install it to process PDF files.")
        try:
            from io import BytesIO
            reader = PyPDF2.PdfReader(BytesIO(content_bytes))
            text_parts = []
            for page_num in range(len(reader.pages)):
                try:
                    page_text = reader.pages[page_num].extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e: # PyPDF2 can sometimes fail on specific pages
                    logger.warning(f"Could not extract text from page {page_num + 1} of {source_name}: {e}")
            return "\n".join(text_parts)
        except Exception as e:
            logger.error(f"Error parsing PDF {source_name}: {e}")
            return ""

    def _parse_docx(self, content_bytes: bytes, source_name: str) -> str:
        if not docx:
            logger.error("python-docx is not installed. Cannot parse DOCX files.")
            raise ImportError("python-docx is not installed. Please install it to process DOCX files.")
        try:
            from io import BytesIO
            document = docx.Document(BytesIO(content_bytes))
            return "\n".join([para.text for para in document.paragraphs if para.text.strip()])
        except Exception as e:
            logger.error(f"Error parsing DOCX {source_name}: {e}")
            return ""

    def _parse_markdown(self, text_content: str, source_name: str) -> str:
        if not md_parser or not BeautifulSoup: # BeautifulSoup for stripping HTML
            logger.warning("Markdown or BeautifulSoup4 not installed. Markdown parsing will be basic (raw content).")
            return text_content
        try:
            html = md_parser.markdown(text_content)
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Error parsing Markdown {source_name}: {e}")
            return text_content # Fallback to original text

    def _parse_html(self, text_content: str, source_name: str) -> str:
        if not BeautifulSoup:
            logger.error("BeautifulSoup4 is not installed. Cannot parse HTML files.")
            raise ImportError("BeautifulSoup4 is not installed. Please install it to process HTML files.")
        try:
            soup = BeautifulSoup(text_content, "html.parser")
            for script_or_style in soup(["script", "style", "header", "footer", "nav", "aside"]): # Remove common non-content tags
                script_or_style.decompose()
            return soup.get_text(separator="\n", strip=True)
        except Exception as e:
            logger.error(f"Error parsing HTML {source_name}: {e}")
            return ""

    async def _fetch_url_content(self, url: HttpUrl) -> Tuple[Optional[bytes], Optional[str], Optional[str]]:
        # Returns (content_bytes, content_type, error_message)
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                logger.info(f"Fetching URL: {url}")
                response = await client.get(str(url))
                response.raise_for_status() # Raise HTTPStatusError for 4xx/5xx
                content_type = response.headers.get("content-type", "").split(";")[0].strip()
                logger.info(f"URL {url} fetched successfully. Content-Type: {content_type}, Status: {response.status_code}")
                return response.content, content_type, None
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code} fetching {url}: {e.response.text[:200]}"
            logger.error(error_msg)
            return None, None, error_msg
        except httpx.RequestError as e: # Covers network errors, DNS failures, timeouts
            error_msg = f"Request error fetching {url}: {type(e).__name__} - {str(e)[:200]}"
            logger.error(error_msg)
            return None, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error fetching {url}: {type(e).__name__} - {str(e)[:200]}"
            logger.error(error_msg)
            return None, None, error_msg

    async def extract_content_from_source(self, source: DocumentSource) -> Tuple[Optional[DocumentContent], Optional[str]]:
        # Returns (DocumentContent, error_message)
        content_bytes: Optional[bytes] = None
        file_name_for_meta = source.file_name # Use provided filename if available
        error_message: Optional[str] = None

        if source.file_path:
            file_name_for_meta = file_name_for_meta or Path(source.file_path).name
            try:
                with open(source.file_path, "rb") as f:
                    content_bytes = f.read()
                logger.info(f"Read {len(content_bytes)} bytes from {source.file_path}")
            except Exception as e:
                error_message = f"Error reading file {source.file_path}: {e}"
                logger.error(error_message)
                return None, error_message
        elif source.url:
            file_name_for_meta = file_name_for_meta or str(source.url).split('/')[-1] or "web_document"
            content_bytes, detected_mime_type, fetch_error = await self._fetch_url_content(source.url)
            if fetch_error or not content_bytes:
                return None, fetch_error or "Failed to fetch content from URL."
        elif source.content_bytes:
            content_bytes = source.content_bytes
            if not file_name_for_meta:
                 error_message = "File name is required when providing content_bytes."
                 logger.error(error_message)
                 return None, error_message
            logger.info(f"Processing {len(content_bytes)} bytes from content_bytes for {file_name_for_meta}")
        else:
            error_message = "No valid document source provided (file_path, url, or content_bytes)."
            logger.error(error_message)
            return None, error_message

        doc_type = self._detect_document_type(source, content_bytes)
        source_name_for_parsing = file_name_for_meta or "unknown_source"
        raw_text = ""

        try:
            if doc_type == DocumentType.PDF:
                raw_text = self._parse_pdf(content_bytes, source_name_for_parsing)
            elif doc_type == DocumentType.DOCX:
                raw_text = self._parse_docx(content_bytes, source_name_for_parsing)
            elif doc_type == DocumentType.MARKDOWN:
                raw_text = self._parse_markdown(content_bytes.decode('utf-8', errors='ignore'), source_name_for_parsing)
            elif doc_type == DocumentType.HTML:
                raw_text = self._parse_html(content_bytes.decode('utf-8', errors='ignore'), source_name_for_parsing)
            elif doc_type in [DocumentType.TXT, DocumentType.PYTHON, DocumentType.JSON, DocumentType.YAML]:
                raw_text = content_bytes.decode('utf-8', errors='ignore')
            else: # UNKNOWN or unhandled
                logger.warning(f"No specific parser for {doc_type} of file {source_name_for_parsing}. Trying plain text.")
                raw_text = content_bytes.decode('utf-8', errors='ignore')
        except ImportError as e: # Catch if a parser was not installed
            error_message = f"Missing parser for {doc_type}: {e}"
            logger.error(error_message)
            return None, error_message
        except Exception as e: # Catch other parsing errors
            error_message = f"Failed to parse {source_name_for_parsing} as {doc_type}: {e}"
            logger.exception(error_message) # Log with stack trace
            return None, error_message

        if not raw_text.strip():
            # This case is handled in process_document to determine overall status
            logger.warning(f"No text extracted from {source_name_for_parsing} (type: {doc_type}).")
            # It's not an error at this stage, but quality validation will catch it.

        metadata = self._extract_metadata(source, doc_type, content_bytes)
        metadata.word_count = len(raw_text.split())

        return DocumentContent(raw_text=raw_text, metadata=metadata, document_type=doc_type), None

    def chunk_content(self, text: str, document_id: str) -> List[ContentChunk]:
        if not text.strip():
            return []
        try:
            # Langchain's text splitter can sometimes add metadata if configured (e.g. start_index)
            # We'll handle metadata more explicitly if needed.
            split_texts = self.text_splitter.split_text(text)
            return [
                ContentChunk(text=chunk_text, document_id=document_id, order=i, metadata={}) # Ensure metadata is dict
                for i, chunk_text in enumerate(split_texts)
                if chunk_text.strip()
            ]
        except Exception as e:
            logger.exception(f"Error chunking content for document {document_id}: {e}")
            return []


    async def generate_embeddings(self, chunks: List[ContentChunk], embedding_model_name: str = "text-embedding-ada-002") -> Tuple[Optional[List[EmbeddedChunk]], Optional[str]]:
        if not chunks:
            return [], None

        chunk_texts = [chunk.text for chunk in chunks]
        try:
            embeddings = await self.model_manager.get_embeddings(chunk_texts, model_name=embedding_model_name)
        except Exception as e:
            error_msg = f"Failed to generate embeddings: {e}"
            logger.exception(error_msg)
            return None, error_msg

        if len(embeddings) != len(chunks):
            error_msg = f"Mismatch between number of chunks ({len(chunks)}) and embeddings ({len(embeddings)})."
            logger.error(error_msg)
            return None, error_msg

        embedded_chunks = []
        for i, chunk in enumerate(chunks):
            embedded_chunks.append(
                EmbeddedChunk(
                    **(chunk.model_dump()), # Use model_dump() for Pydantic v2
                    embedding=embeddings[i],
                    embedding_model_name=embedding_model_name
                )
            )
        return embedded_chunks, None

    def validate_content_quality(self, content: Optional[DocumentContent], chunks: Optional[List[ContentChunk]]) -> QualityScore:
        issues = []
        if not content or not content.raw_text.strip():
            issues.append("No content extracted or content is empty.")
            return QualityScore(overall_score=0.0, completeness=0.0, clarity=0.0, potential_issues=issues)

        completeness = 1.0 if len(content.raw_text) > 50 else len(content.raw_text) / 50.0 # Min 50 chars for some completeness
        clarity = 1.0 # Placeholder for now

        if not chunks or len(chunks) == 0 :
            if content.raw_text.strip():
                 issues.append("Content could not be chunked effectively (e.g., too short or uniform).")
                 completeness = min(completeness, 0.2)

        overall = (completeness + clarity) / 2
        if issues:
            overall = max(0.0, overall - 0.25 * len(issues))

        return QualityScore(
            overall_score=min(1.0, max(0.0, overall)),
            completeness=min(1.0, max(0.0, completeness)),
            clarity=min(1.0, max(0.0, clarity)),
            potential_issues=issues
        )

    async def store_in_knowledge_base(self, processed_doc_entry: ProcessedDocumentEntry, embedded_chunks: List[EmbeddedChunk]) -> Optional[str]:
        if not embedded_chunks:
            logger.info(f"No embedded chunks to store for document {processed_doc_entry.id}")
            return None

        kb_entries = []
        for chunk in embedded_chunks:
            entry = KnowledgeBaseEntry(
                processed_document_id=processed_doc_entry.id,
                document_source_name=processed_doc_entry.source_file_name or processed_doc_entry.source_url or "unknown_source",
                chunk_order=chunk.order,
                content=chunk.text,
                embedding=chunk.embedding,
                embedding_model_name=chunk.embedding_model_name,
                metadata=chunk.metadata,
                document_metadata=processed_doc_entry.metadata or {},
                document_quality_score=processed_doc_entry.quality_score.get("overall_score", 0.0) if processed_doc_entry.quality_score else 0.0,
            )
            kb_entries.append(entry)

        try:
            await self.supabase_client.upsert_knowledge_base_entries(kb_entries)
            logger.info(f"Stored {len(kb_entries)} chunks for document {processed_doc_entry.id} in knowledge base.")
            return None
        except Exception as e:
            error_msg = f"Failed to store knowledge base entries for doc {processed_doc_entry.id}: {e}"
            logger.exception(error_msg)
            return error_msg

    async def process_document(self, source: DocumentSource) -> ProcessingResult:
        start_time = time.time()
        source_display_name = source.file_name or (Path(source.file_path).name if source.file_path else str(source.url) if source.url else "bytes_content")

        # Initial ProcessedDocumentEntry
        processed_doc_entry = ProcessedDocumentEntry(
            source_file_path=str(source.file_path) if source.file_path else None,
            source_url=str(source.url) if source.url else None,
            source_file_name=source_display_name, # Use the display name here
            document_type=DocumentType.UNKNOWN, # Will be updated after detection
            status=ProcessingStatus.PENDING,
            processing_started_at=datetime.datetime.utcnow()
        )

        final_status = ProcessingStatus.FAILURE
        error_message_final: Optional[str] = "Unknown processing error."
        doc_content_final: Optional[DocumentContent] = None
        chunks_final: Optional[List[ContentChunk]] = None
        embedded_chunks_final: Optional[List[EmbeddedChunk]] = None
        quality_score_final: Optional[QualityScore] = None

        try:
            logger.info(f"Processing document: {source_display_name}")
            doc_content_final, extraction_error = await self.extract_content_from_source(source)

            if extraction_error or not doc_content_final:
                error_message_final = extraction_error or f"Failed to extract content from {source_display_name}."
                logger.error(error_message_final)
                # Quality score even if extraction fails, based on None content
                quality_score_final = self.validate_content_quality(None, None)
                # processed_doc_entry is already PENDING, will be updated to FAILURE finally
            else:
                processed_doc_entry.document_type = doc_content_final.document_type # Update detected type
                processed_doc_entry.metadata = doc_content_final.metadata.model_dump()

                if not doc_content_final.raw_text.strip():
                    error_message_final = f"Extracted content from {source_display_name} is empty."
                    logger.warning(error_message_final)
                    # Quality score for empty content
                    quality_score_final = self.validate_content_quality(doc_content_final, None)
                    # This might be a partial success or failure depending on policy
                    final_status = ProcessingStatus.FAILURE # Treat as failure if no text
                else:
                    chunks_final = self.chunk_content(doc_content_final.raw_text, processed_doc_entry.id)
                    processed_doc_entry.chunk_count = len(chunks_final)

                    if not chunks_final:
                         logger.warning(f"No content chunks generated for {source_display_name}. Document might be too small or empty after cleaning.")

                    embedded_chunks_final, embedding_error = await self.generate_embeddings(chunks_final)
                    if embedding_error:
                        error_message_final = embedding_error
                        final_status = ProcessingStatus.PARTIAL_SUCCESS # Content extracted, but embedding failed
                    elif embedded_chunks_final is not None: # Check for None in case of non-error empty list
                        processed_doc_entry.embedded_chunk_count = len(embedded_chunks_final)

                    quality_score_final = self.validate_content_quality(doc_content_final, chunks_final)

                    if not error_message_final and quality_score_final.overall_score < 0.1: # Stricter quality gate
                        error_message_final = f"Document {source_display_name} has very low quality ({quality_score_final.overall_score}). Not storing in KB."
                        logger.warning(error_message_final)
                        final_status = ProcessingStatus.FAILURE # Treat as failure if too low quality
                    elif not error_message_final: # Store if no errors so far and quality is acceptable
                        storage_error = await self.store_in_knowledge_base(processed_doc_entry, embedded_chunks_final or [])
                        if storage_error:
                            error_message_final = storage_error
                            final_status = ProcessingStatus.PARTIAL_SUCCESS # Storing failed
                        else:
                            final_status = ProcessingStatus.SUCCESS
                            error_message_final = None # Clear any previous warnings if overall success

            # Update ProcessedDocumentEntry status and details
            processed_doc_entry.status = final_status
            processed_doc_entry.error_message = error_message_final
            processed_doc_entry.quality_score = quality_score_final.model_dump() if quality_score_final else None
            processed_doc_entry.processing_time_seconds = time.time() - start_time
            processed_doc_entry.processing_ended_at = datetime.datetime.utcnow()

            await self.supabase_client.upsert_processed_document(processed_doc_entry)

            return ProcessingResult(
                document_id=processed_doc_entry.id,
                source_display_name=source_display_name,
                extracted_content=doc_content_final,
                chunks=chunks_final,
                embedded_chunks=embedded_chunks_final,
                quality_score=quality_score_final,
                processing_time_seconds=processed_doc_entry.processing_time_seconds,
                status=final_status,
                error_message=error_message_final,
                chunk_count=processed_doc_entry.chunk_count,
                embedded_chunk_count=processed_doc_entry.embedded_chunk_count
            )

        except Exception as e:
            logger.exception(f"Unhandled error processing document {source_display_name}: {e}")
            processing_time = time.time() - start_time
            processed_doc_entry.status = ProcessingStatus.FAILURE
            processed_doc_entry.error_message = f"Unhandled: {str(e)}"
            processed_doc_entry.processing_time_seconds = processing_time
            processed_doc_entry.processing_ended_at = datetime.datetime.utcnow()
            if quality_score_final: # If quality score was calculated before exception
                 processed_doc_entry.quality_score = quality_score_final.model_dump()
            else: # Calculate a basic failure score
                 processed_doc_entry.quality_score = self.validate_content_quality(None, None).model_dump()


            try:
                await self.supabase_client.upsert_processed_document(processed_doc_entry)
            except Exception as db_e:
                logger.error(f"Failed to update Supabase with error status for {processed_doc_entry.id}: {db_e}")

            return ProcessingResult(
                document_id=processed_doc_entry.id,
                source_display_name=source_display_name,
                status=ProcessingStatus.FAILURE,
                error_message=processed_doc_entry.error_message,
                processing_time_seconds=processing_time,
                quality_score=QualityScore.model_validate(processed_doc_entry.quality_score) if processed_doc_entry.quality_score else None
            )

    async def process_batch(self, sources: List[DocumentSource]) -> List[ProcessingResult]:
        # Using asyncio.gather to run process_document concurrently for all sources
        results = await asyncio.gather(
            *[self.process_document(source) for source in sources],
            return_exceptions=True # Allow individual tasks to fail without stopping others
        )

        # Handle cases where asyncio.gather itself might have returned exceptions
        final_results = []
        for i, res_or_exc in enumerate(results):
            source_display_name = sources[i].file_name or (Path(sources[i].file_path).name if sources[i].file_path else str(sources[i].url) if sources[i].url else "bytes_content")
            if isinstance(res_or_exc, Exception):
                logger.error(f"Exception during batch processing for {source_display_name}: {res_or_exc}")
                final_results.append(ProcessingResult(
                    document_id=str(uuid.uuid4()), # Generate a temp ID
                    source_display_name=source_display_name,
                    status=ProcessingStatus.FAILURE,
                    error_message=f"Batch task failed: {str(res_or_exc)}",
                    processing_time_seconds=0.0 # Could try to measure if needed
                ))
            else:
                final_results.append(res_or_exc)
        return final_results
