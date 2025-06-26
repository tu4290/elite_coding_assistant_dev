import asyncio
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, ANY

from main.document_ingestion_system import DocumentIngestionSystem, SupabaseLearningClient, ModelManager
from main.models.document_processing import (
    DocumentSource, DocumentType, ProcessingStatus,
    ProcessedDocumentEntry, KnowledgeBaseEntry
)

# Concrete mock classes for this integration test
class IntegrationMockSupabaseClient(SupabaseLearningClient):
    def __init__(self):
        self.processed_documents_store = {}
        self.knowledge_base_store = [] # Stores all KBEs from all docs

    async def upsert_processed_document(self, doc_entry: ProcessedDocumentEntry) -> Dict[str, Any]:
        self.processed_documents_store[doc_entry.id] = doc_entry.model_dump_json() # Store as JSON string for simplicity
        return {"id": doc_entry.id, "status": "success", "data": [doc_entry.model_dump()]} # Supabase client often returns list

    async def upsert_knowledge_base_entries(self, entries: List[KnowledgeBaseEntry]) -> Dict[str, Any]:
        self.knowledge_base_store.extend([entry.model_dump_json() for entry in entries])
        return {"count": len(entries), "status": "success", "data": [entry.model_dump() for entry in entries]}

    def get_processed_document_by_id(self, doc_id: str) -> Optional[ProcessedDocumentEntry]:
        data_json = self.processed_documents_store.get(doc_id)
        return ProcessedDocumentEntry.model_validate_json(data_json) if data_json else None

    def get_knowledge_base_entries_for_doc(self, doc_id: str) -> List[KnowledgeBaseEntry]:
        return [KnowledgeBaseEntry.model_validate_json(entry_json) for entry_json in self.knowledge_base_store if KnowledgeBaseEntry.model_validate_json(entry_json).processed_document_id == doc_id]


class IntegrationMockModelManager(ModelManager):
    def __init__(self, embedding_dim=3): # Allow customizing embedding dim for tests
        self.embedding_dim = embedding_dim

    async def get_embeddings(self, texts: List[str], model_name: str = "test_embedding_model") -> List[List[float]]:
        # Generate simple, predictable embeddings based on text length and index
        embeddings = []
        for i, text in enumerate(texts):
            base_val = len(text) / 100.0 + i * 0.1
            embedding = [(base_val + j * 0.01) % 1.0 for j in range(self.embedding_dim)]
            embeddings.append(embedding)
        return embeddings

@pytest.fixture
def mock_supabase_client_integration():
    return IntegrationMockSupabaseClient()

@pytest.fixture
def mock_model_manager_integration():
    return IntegrationMockModelManager(embedding_dim=1536) # Match typical embedding sizes

@pytest.fixture
def ingestion_system_integration(mock_supabase_client_integration, mock_model_manager_integration):
    return DocumentIngestionSystem(mock_supabase_client_integration, mock_model_manager_integration)

@pytest.mark.asyncio
async def test_full_ingestion_flow_txt_file(
    ingestion_system_integration: DocumentIngestionSystem,
    mock_supabase_client_integration: IntegrationMockSupabaseClient,
    mock_model_manager_integration: IntegrationMockModelManager,
    tmp_path
):
    file_content = "This is a test document for integration testing.\nIt contains several sentences and spans multiple lines to ensure chunking works as expected."
    test_file = tmp_path / "integration_test.txt"
    test_file.write_text(file_content)

    source = DocumentSource(file_path=test_file, file_name="integration_test.txt")

    # Spy on the actual methods of the concrete mocks
    mock_supabase_client_integration.upsert_processed_document = AsyncMock(wraps=mock_supabase_client_integration.upsert_processed_document)
    mock_supabase_client_integration.upsert_knowledge_base_entries = AsyncMock(wraps=mock_supabase_client_integration.upsert_knowledge_base_entries)
    mock_model_manager_integration.get_embeddings = AsyncMock(wraps=mock_model_manager_integration.get_embeddings)

    result = await ingestion_system_integration.process_document(source)

    # 1. Check ProcessingResult
    assert result.status == ProcessingStatus.SUCCESS
    assert result.document_id is not None
    assert result.source_display_name == "integration_test.txt"
    assert result.extracted_content is not None
    assert result.extracted_content.raw_text == file_content
    assert result.extracted_content.document_type == DocumentType.TXT
    assert result.chunk_count > 0
    assert result.embedded_chunk_count == result.chunk_count
    assert result.quality_score.overall_score > 0.5

    # 2. Verify ModelManager interaction
    mock_model_manager_integration.get_embeddings.assert_called_once()
    # Check that the number of texts passed to get_embeddings matches chunk_count
    texts_for_embedding = mock_model_manager_integration.get_embeddings.call_args[0][0]
    assert len(texts_for_embedding) == result.chunk_count

    # 3. Verify Supabase interactions
    mock_supabase_client_integration.upsert_processed_document.assert_called_once()
    processed_doc_entry_arg = mock_supabase_client_integration.upsert_processed_document.call_args[0][0]
    assert isinstance(processed_doc_entry_arg, ProcessedDocumentEntry)
    assert processed_doc_entry_arg.id == result.document_id
    assert processed_doc_entry_arg.source_file_name == "integration_test.txt"
    assert processed_doc_entry_arg.status == ProcessingStatus.SUCCESS
    assert processed_doc_entry_arg.chunk_count == result.chunk_count
    assert processed_doc_entry_arg.embedded_chunk_count == result.embedded_chunk_count

    if result.chunk_count > 0 :
        mock_supabase_client_integration.upsert_knowledge_base_entries.assert_called_once()
        kb_entries_arg = mock_supabase_client_integration.upsert_knowledge_base_entries.call_args[0][0]
        assert len(kb_entries_arg) == result.chunk_count
        for entry in kb_entries_arg:
            assert isinstance(entry, KnowledgeBaseEntry)
            assert entry.processed_document_id == result.document_id
            assert entry.embedding is not None
            assert len(entry.embedding) == 1536 # Matches mock_model_manager_integration
            assert entry.embedding_model_name == "test_embedding_model" # Default from mock
    else:
        mock_supabase_client_integration.upsert_knowledge_base_entries.assert_not_called()


    # 4. Verify data stored in mock Supabase (optional, but good for integration test)
    stored_proc_doc = mock_supabase_client_integration.get_processed_document_by_id(result.document_id)
    assert stored_proc_doc is not None
    assert stored_proc_doc.source_file_name == "integration_test.txt"

    stored_kb_entries = mock_supabase_client_integration.get_knowledge_base_entries_for_doc(result.document_id)
    assert len(stored_kb_entries) == result.chunk_count
    if result.chunk_count > 0:
        assert stored_kb_entries[0].content.strip() != ""

@pytest.mark.asyncio
async def test_ingestion_failure_handling(
    ingestion_system_integration: DocumentIngestionSystem,
    mock_supabase_client_integration: IntegrationMockSupabaseClient
):
    source = DocumentSource(file_path="non_existent_file_for_integration.txt", file_name="non_existent_file_for_integration.txt")

    # Spy on upsert_processed_document
    mock_supabase_client_integration.upsert_processed_document = AsyncMock(wraps=mock_supabase_client_integration.upsert_processed_document)

    result = await ingestion_system_integration.process_document(source)

    assert result.status == ProcessingStatus.FAILURE
    assert "Error reading file" in result.error_message
    assert result.document_id is not None # An ID should still be generated for the ProcessedDocumentEntry

    # Verify that the failure was recorded in Supabase
    mock_supabase_client_integration.upsert_processed_document.assert_called_once()
    processed_doc_entry_arg = mock_supabase_client_integration.upsert_processed_document.call_args[0][0]
    assert processed_doc_entry_arg.id == result.document_id
    assert processed_doc_entry_arg.status == ProcessingStatus.FAILURE
    assert "Error reading file" in processed_doc_entry_arg.error_message

    # Check that no KBEs were attempted to be stored
    stored_kb_entries = mock_supabase_client_integration.get_knowledge_base_entries_for_doc(result.document_id)
    assert len(stored_kb_entries) == 0

@pytest.mark.asyncio
async def test_ingestion_empty_content_after_parsing(
    ingestion_system_integration: DocumentIngestionSystem,
    mock_supabase_client_integration: IntegrationMockSupabaseClient,
    tmp_path
):
    # Create a file that might result in empty content after parsing (e.g., PDF with only images, or specific HTML)
    # For simplicity, we'll mock the parser to return empty.
    empty_content_file = tmp_path / "empty_content.pdf" # Type doesn't matter due to mocking below
    empty_content_file.write_text("Fake content that parser will ignore")

    source = DocumentSource(file_path=empty_content_file, file_name="empty_content.pdf")

    # Mock the specific parser to return empty string
    with patch.object(ingestion_system_integration, '_parse_pdf', return_value=""): # Assuming it's detected as PDF
        # Spy on upsert_processed_document
        mock_supabase_client_integration.upsert_processed_document = AsyncMock(wraps=mock_supabase_client_integration.upsert_processed_document)

        result = await ingestion_system_integration.process_document(source)

    assert result.status == ProcessingStatus.FAILURE # Or SUCCESS with 0 score, depending on strictness
    assert "Failed to extract text content" in result.error_message # Current behavior
    assert result.quality_score.overall_score == 0.0
    assert result.chunk_count == 0
    assert result.embedded_chunk_count == 0

    # Verify that the failure/low quality was recorded
    mock_supabase_client_integration.upsert_processed_document.assert_called_once()
    processed_doc_entry_arg = mock_supabase_client_integration.upsert_processed_document.call_args[0][0]
    assert processed_doc_entry_arg.status == ProcessingStatus.FAILURE
    assert processed_doc_entry_arg.quality_score['overall_score'] == 0.0
    assert processed_doc_entry_arg.chunk_count == 0


@pytest.mark.asyncio
async def test_batch_processing_integration(
    ingestion_system_integration: DocumentIngestionSystem,
    mock_supabase_client_integration: IntegrationMockSupabaseClient,
    tmp_path
):
    file1_content = "First document for batch processing."
    file1 = tmp_path / "batch1.txt"
    file1.write_text(file1_content)
    source1 = DocumentSource(file_path=file1, file_name="batch1.txt")

    file2_content = "Second document, slightly longer, for batch testing."
    file2 = tmp_path / "batch2.txt"
    file2.write_text(file2_content)
    source2 = DocumentSource(file_path=file2, file_name="batch2.txt")

    source_fail = DocumentSource(file_path="non_existent_batch.txt", file_name="non_existent_batch.txt")

    # Spy
    mock_supabase_client_integration.upsert_processed_document = AsyncMock(wraps=mock_supabase_client_integration.upsert_processed_document)
    mock_supabase_client_integration.upsert_knowledge_base_entries = AsyncMock(wraps=mock_supabase_client_integration.upsert_knowledge_base_entries)

    results = await ingestion_system_integration.process_batch([source1, source2, source_fail])

    assert len(results) == 3

    success_results = [r for r in results if r.status == ProcessingStatus.SUCCESS]
    failure_results = [r for r in results if r.status == ProcessingStatus.FAILURE]

    assert len(success_results) == 2
    assert len(failure_results) == 1

    assert success_results[0].source_display_name == "batch1.txt"
    assert success_results[1].source_display_name == "batch2.txt"
    assert failure_results[0].source_display_name == "non_existent_batch.txt"

    # Check Supabase calls
    # upsert_processed_document should be called for each document
    assert mock_supabase_client_integration.upsert_processed_document.call_count == 3

    # upsert_knowledge_base_entries should be called for each successful document with chunks
    successful_chunk_uploads = sum(1 for r in success_results if r.chunk_count > 0)
    assert mock_supabase_client_integration.upsert_knowledge_base_entries.call_count == successful_chunk_uploads

    # Verify data in mock Supabase
    proc_doc1 = mock_supabase_client_integration.get_processed_document_by_id(success_results[0].document_id)
    assert proc_doc1 is not None
    assert proc_doc1.status == ProcessingStatus.SUCCESS

    proc_doc_fail = mock_supabase_client_integration.get_processed_document_by_id(failure_results[0].document_id)
    assert proc_doc_fail is not None
    assert proc_doc_fail.status == ProcessingStatus.FAILURE

    kb_entries_doc1 = mock_supabase_client_integration.get_knowledge_base_entries_for_doc(success_results[0].document_id)
    assert len(kb_entries_doc1) == success_results[0].chunk_count
    if kb_entries_doc1:
         assert kb_entries_doc1[0].content.strip() != ""
