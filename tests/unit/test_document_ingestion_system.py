import asyncio
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open

from main.document_ingestion_system import DocumentIngestionSystem
from main.models.document_processing import (
    DocumentSource, DocumentType, ProcessingStatus,
    DocumentContent, DocumentMetadata, ContentChunk
)

# Mock classes for dependencies
class MockSupabaseLearningClient:
    async def upsert_processed_document(self, doc_entry):
        return {"id": doc_entry.id, "status": "success"}

    async def upsert_knowledge_base_entries(self, entries):
        return {"count": len(entries), "status": "success"}

class MockModelManager:
    async def get_embeddings(self, texts, model_name="default_embedding_model"):
        # Return embeddings of consistent dimensionality (e.g., 3 for simplicity in tests)
        return [[0.1, 0.2, 0.3] for _ in texts]

@pytest.fixture
def mock_supabase_client():
    client = MockSupabaseLearningClient()
    client.upsert_processed_document = AsyncMock(wraps=client.upsert_processed_document)
    client.upsert_knowledge_base_entries = AsyncMock(wraps=client.upsert_knowledge_base_entries)
    return client

@pytest.fixture
def mock_model_manager():
    manager = MockModelManager()
    manager.get_embeddings = AsyncMock(wraps=manager.get_embeddings)
    return manager

@pytest.fixture
def ingestion_system(mock_supabase_client, mock_model_manager):
    return DocumentIngestionSystem(mock_supabase_client, mock_model_manager)

@pytest.mark.asyncio
async def test_process_document_txt_file_success(ingestion_system: DocumentIngestionSystem, tmp_path):
    # Create a dummy text file
    file_content = "This is a simple test text file.\nIt has two lines."
    test_file = tmp_path / "test_doc.txt"
    test_file.write_text(file_content)

    source = DocumentSource(file_path=test_file, file_name="test_doc.txt")
    result = await ingestion_system.process_document(source)

    assert result.status == ProcessingStatus.SUCCESS
    assert result.document_id is not None
    assert result.source_display_name == "test_doc.txt"
    assert result.extracted_content is not None
    assert result.extracted_content.raw_text == file_content
    assert result.extracted_content.document_type == DocumentType.TXT
    assert result.chunks is not None
    assert len(result.chunks) > 0
    assert result.embedded_chunks is not None
    assert len(result.embedded_chunks) == len(result.chunks)
    assert result.quality_score is not None
    assert result.quality_score.overall_score > 0.5 # Basic check

    ingestion_system.supabase_client.upsert_processed_document.assert_called_once()
    ingestion_system.supabase_client.upsert_knowledge_base_entries.assert_called_once()
    ingestion_system.model_manager.get_embeddings.assert_called_once()

@pytest.mark.asyncio
async def test_process_document_empty_file(ingestion_system: DocumentIngestionSystem, tmp_path):
    test_file = tmp_path / "empty.txt"
    test_file.write_text("") # Empty file

    source = DocumentSource(file_path=test_file, file_name="empty.txt")
    result = await ingestion_system.process_document(source)

    assert result.status == ProcessingStatus.FAILURE # Or SUCCESS with low quality and no chunks
    # Depending on how strict we want to be. Current implementation leads to failure if no content.
    assert "Failed to extract text content" in result.error_message
    assert result.quality_score.overall_score == 0.0

@pytest.mark.asyncio
async def test_process_document_non_existent_file(ingestion_system: DocumentIngestionSystem):
    source = DocumentSource(file_path="non_existent_file.txt", file_name="non_existent_file.txt")
    result = await ingestion_system.process_document(source)

    assert result.status == ProcessingStatus.FAILURE
    assert "Error reading file" in result.error_message

@pytest.mark.asyncio
async def test_process_document_unsupported_type_by_extension(ingestion_system: DocumentIngestionSystem, tmp_path):
    test_file = tmp_path / "test.unsupported"
    test_file.write_text("Some content")

    source = DocumentSource(file_path=test_file, file_name="test.unsupported")
    result = await ingestion_system.process_document(source)

    # It should try to parse as text and likely succeed if it's text-based
    assert result.status == ProcessingStatus.SUCCESS
    assert result.extracted_content.document_type == DocumentType.UNKNOWN # or TXT if magic detects it
    assert result.extracted_content.raw_text == "Some content"

@pytest.mark.asyncio
@patch('main.document_ingestion_system.httpx.AsyncClient')
async def test_process_document_url_success(mock_async_client, ingestion_system: DocumentIngestionSystem):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"content-type": "text/plain; charset=utf-8"}
    mock_response.content = b"Content from URL."

    # Configure the mock client instance's get method
    mock_get = AsyncMock(return_value=mock_response)
    mock_async_client.return_value.__aenter__.return_value.get = mock_get

    source = DocumentSource(url="http://example.com/test.txt", file_name="test.txt")
    result = await ingestion_system.process_document(source)

    assert result.status == ProcessingStatus.SUCCESS
    assert result.extracted_content.raw_text == "Content from URL."
    assert result.extracted_content.document_type == DocumentType.TXT
    mock_get.assert_called_once_with("http://example.com/test.txt", follow_redirects=True, timeout=30.0)

@pytest.mark.asyncio
@patch('main.document_ingestion_system.httpx.AsyncClient')
async def test_process_document_url_failure(mock_async_client, ingestion_system: DocumentIngestionSystem):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"

    mock_exception = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=mock_response)
    mock_get = AsyncMock(side_effect=mock_exception)
    mock_async_client.return_value.__aenter__.return_value.get = mock_get

    source = DocumentSource(url="http://example.com/notfound.txt", file_name="notfound.txt")
    result = await ingestion_system.process_document(source)

    assert result.status == ProcessingStatus.FAILURE
    assert "Failed to extract text content" in result.error_message # Because _fetch_url_content returns None

@pytest.mark.asyncio
async def test_process_document_content_bytes_success(ingestion_system: DocumentIngestionSystem):
    byte_content = b"This is a byte string document content for testing."
    source = DocumentSource(content_bytes=byte_content, file_name="bytes_doc.txt", document_type=DocumentType.TXT)
    result = await ingestion_system.process_document(source)

    assert result.status == ProcessingStatus.SUCCESS
    assert result.extracted_content.raw_text == "This is a byte string document content for testing."
    assert result.extracted_content.document_type == DocumentType.TXT

def test_detect_document_type_by_extension(ingestion_system: DocumentIngestionSystem):
    source_pdf = DocumentSource(file_name="doc.pdf")
    assert ingestion_system._detect_document_type(source_pdf) == DocumentType.PDF

    source_py = DocumentSource(file_name="script.py")
    assert ingestion_system._detect_document_type(source_py) == DocumentType.PYTHON

    source_unknown = DocumentSource(file_name="archive.zip")
    # Without magic, this would be UNKNOWN. With magic, it might differ.
    # For unit test, assuming magic might not be perfectly mocked or available.
    with patch('main.document_ingestion_system.magic', None): # Simulate magic not installed
         assert ingestion_system._detect_document_type(source_unknown, b"PK...") == DocumentType.UNKNOWN


@patch('main.document_ingestion_system.magic')
def test_detect_document_type_with_magic(mock_magic, ingestion_system: DocumentIngestionSystem):
    mock_magic.from_buffer.return_value = "application/pdf"
    source = DocumentSource(file_name="no_ext_file")
    assert ingestion_system._detect_document_type(source, b"%PDF-1.4...") == DocumentType.PDF
    mock_magic.from_buffer.assert_called_once_with(b"%PDF-1.4...", mime=True)

def test_chunk_content(ingestion_system: DocumentIngestionSystem):
    text = "This is the first sentence. This is the second sentence. This is the third sentence, which is a bit longer."
    # Configure splitter for predictable chunks in test if necessary, or use default
    ingestion_system.text_splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=5)
    chunks = ingestion_system.chunk_content(text, document_id="doc1")

    assert len(chunks) > 1
    assert isinstance(chunks[0], ContentChunk)
    assert chunks[0].text.strip() != ""
    assert chunks[0].document_id == "doc1"
    assert chunks[0].order == 0

def test_chunk_content_empty_text(ingestion_system: DocumentIngestionSystem):
    chunks = ingestion_system.chunk_content("", document_id="doc_empty")
    assert len(chunks) == 0

@pytest.mark.asyncio
async def test_generate_embeddings(ingestion_system: DocumentIngestionSystem):
    chunks = [
        ContentChunk(text="chunk 1 text", document_id="doc1", order=0),
        ContentChunk(text="chunk 2 text", document_id="doc1", order=1),
    ]
    embedded_chunks = await ingestion_system.generate_embeddings(chunks, "test_model")

    assert len(embedded_chunks) == 2
    assert embedded_chunks[0].embedding == [0.1, 0.2, 0.3] # From mock
    assert embedded_chunks[0].embedding_model_name == "test_model"
    assert embedded_chunks[0].text == "chunk 1 text"

def test_validate_content_quality_good(ingestion_system: DocumentIngestionSystem):
    doc_content = DocumentContent(
        raw_text="This is a good quality document with sufficient text.",
        metadata=DocumentMetadata(title="Good Doc"),
        document_type=DocumentType.TXT
    )
    chunks = [ContentChunk(text="good chunk", document_id="doc1", order=0)]
    quality = ingestion_system.validate_content_quality(doc_content, chunks)
    assert quality.overall_score > 0.7
    assert not quality.potential_issues

def test_validate_content_quality_poor_empty(ingestion_system: DocumentIngestionSystem):
    doc_content = DocumentContent(
        raw_text="  ", # Whitespace only
        metadata=DocumentMetadata(title="Empty Doc"),
        document_type=DocumentType.TXT
    )
    quality = ingestion_system.validate_content_quality(doc_content, [])
    assert quality.overall_score == 0.0
    assert "No content extracted" in quality.potential_issues[0]

def test_validate_content_quality_no_chunks(ingestion_system: DocumentIngestionSystem):
    doc_content = DocumentContent(
        raw_text="Short but has content.",
        metadata=DocumentMetadata(title="Short Doc"),
        document_type=DocumentType.TXT
    )
    # Empty list of chunks when content is present
    quality = ingestion_system.validate_content_quality(doc_content, [])
    assert "Content could not be chunked effectively" in quality.potential_issues
    assert quality.overall_score < 0.6 # Should be penalized

@pytest.mark.asyncio
async def test_process_batch_success_and_failure(ingestion_system: DocumentIngestionSystem, tmp_path):
    # Success file
    success_file = tmp_path / "success.txt"
    success_file.write_text("This is good content.")
    source_success = DocumentSource(file_path=success_file, file_name="success.txt")

    # Failure file (non-existent)
    source_failure = DocumentSource(file_path="non_existent.txt", file_name="non_existent.txt")

    results = await ingestion_system.process_batch([source_success, source_failure])

    assert len(results) == 2
    assert results[0].status == ProcessingStatus.SUCCESS
    assert results[0].source_display_name == "success.txt"
    assert results[1].status == ProcessingStatus.FAILURE
    assert results[1].source_display_name == "non_existent.txt"

# Basic PDF Parsing Test (requires PyPDF2 to be installed in the test env)
@patch('main.document_ingestion_system.PyPDF2')
@pytest.mark.asyncio
async def test_parse_pdf_mocked(mock_pypdf2, ingestion_system: DocumentIngestionSystem, tmp_path):
    if not PyPDF2: # If PyPDF2 is not installed in test env, skip this
        pytest.skip("PyPDF2 not installed, skipping PDF parsing test")

    # Mock PyPDF2's PdfReader
    mock_reader_instance = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "PDF Page 1 content."
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = " PDF Page 2 content."
    mock_reader_instance.pages = [mock_page1, mock_page2]

    # When PdfReader is called with BytesIO(pdf_bytes), it returns our mock_reader_instance
    mock_pypdf2.PdfReader.return_value = mock_reader_instance

    pdf_file = tmp_path / "test.pdf"
    pdf_file.write_bytes(b"dummy pdf content") # Content doesn't matter due to mocking

    source = DocumentSource(file_path=pdf_file, file_name="test.pdf")
    result = await ingestion_system.process_document(source)

    assert result.status == ProcessingStatus.SUCCESS
    assert result.extracted_content.raw_text == "PDF Page 1 content. PDF Page 2 content."
    assert result.extracted_content.document_type == DocumentType.PDF
    mock_pypdf2.PdfReader.assert_called_once()

# Add similar tests for _parse_docx, _parse_markdown, _parse_html by mocking their respective libraries
# For example, for DOCX:
@patch('main.document_ingestion_system.docx')
@pytest.mark.asyncio
async def test_parse_docx_mocked(mock_docx_lib, ingestion_system: DocumentIngestionSystem, tmp_path):
    if not docx:
        pytest.skip("python-docx not installed, skipping DOCX parsing test")

    mock_doc_instance = MagicMock()
    mock_para1 = MagicMock()
    mock_para1.text = "DOCX Paragraph 1."
    mock_para2 = MagicMock()
    mock_para2.text = "DOCX Paragraph 2."
    mock_doc_instance.paragraphs = [mock_para1, mock_para2]
    mock_docx_lib.Document.return_value = mock_doc_instance

    docx_file = tmp_path / "test.docx"
    docx_file.write_bytes(b"dummy docx content")

    source = DocumentSource(file_path=docx_file, file_name="test.docx")
    result = await ingestion_system.process_document(source)

    assert result.status == ProcessingStatus.SUCCESS
    assert result.extracted_content.raw_text == "DOCX Paragraph 1.\nDOCX Paragraph 2."
    assert result.extracted_content.document_type == DocumentType.DOCX
    mock_docx_lib.Document.assert_called_once()

# Test that Supabase client is called correctly
@pytest.mark.asyncio
async def test_store_in_knowledge_base_calls_supabase(ingestion_system: DocumentIngestionSystem):
    doc_entry_mock = MagicMock()
    doc_entry_mock.id = "doc_uuid_123"
    doc_entry_mock.source_file_name = "test_doc.txt"
    doc_entry_mock.metadata = {"title": "Test Doc"}
    doc_entry_mock.quality_score = {"overall_score": 0.8}

    embedded_chunks = [
        EmbeddedChunk(
            text="chunk 1", document_id="doc_uuid_123", order=0,
            embedding=[0.1,0.2,0.3], embedding_model_name="test_model",
            metadata={"page": 1}
        )
    ]
    await ingestion_system.store_in_knowledge_base(doc_entry_mock, embedded_chunks)

    ingestion_system.supabase_client.upsert_knowledge_base_entries.assert_called_once()
    call_args = ingestion_system.supabase_client.upsert_knowledge_base_entries.call_args[0][0]
    assert len(call_args) == 1
    assert call_args[0].content == "chunk 1"
    assert call_args[0].processed_document_id == "doc_uuid_123"
    assert call_args[0].document_metadata == {"title": "Test Doc"}
    assert call_args[0].document_quality_score == 0.8

# Test that ProcessedDocumentEntry is correctly recorded in Supabase
@pytest.mark.asyncio
async def test_process_document_records_processed_document_entry(ingestion_system: DocumentIngestionSystem, tmp_path):
    test_file = tmp_path / "record_test.txt"
    test_file.write_text("Content for recording.")
    source = DocumentSource(file_path=test_file, file_name="record_test.txt")

    await ingestion_system.process_document(source)

    ingestion_system.supabase_client.upsert_processed_document.assert_called_once()
    call_args = ingestion_system.supabase_client.upsert_processed_document.call_args[0][0]

    assert call_args.source_file_name == "record_test.txt"
    assert call_args.status == ProcessingStatus.SUCCESS
    assert call_args.chunk_count > 0
    assert call_args.embedded_chunk_count == call_args.chunk_count
    assert call_args.processing_time_seconds > 0
    assert call_args.quality_score is not None
    assert call_args.metadata is not None
