# Elite Coding Assistant - Testing Documentation

## Overview

This document outlines the comprehensive testing strategy for the Elite Coding Assistant, including unit tests, integration tests, end-to-end tests, performance tests, and security tests.

## Testing Philosophy

Our testing approach follows the **Testing Pyramid** principle:

```mermaid
graph TD
    A["🔺 Testing Pyramid"] --> B["E2E Tests (10%)<br/>UI, User Workflows"]
    B --> C["Integration Tests (20%)<br/>API, Database, Services"]
    C --> D["Unit Tests (70%)<br/>Functions, Classes, Components"]
    
    style B fill:#ff6b6b
    style C fill:#4ecdc4
    style D fill:#45b7d1
```

### Testing Principles

1. **Fast Feedback**: Unit tests run in milliseconds
2. **Reliable**: Tests are deterministic and stable
3. **Maintainable**: Tests are easy to read and update
4. **Comprehensive**: High code coverage with meaningful tests
5. **Isolated**: Tests don't depend on external services

## Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── core/
│   ├── services/
│   ├── utils/
│   └── models/
├── integration/             # Integration tests
│   ├── api/
│   ├── database/
│   └── services/
├── e2e/                     # End-to-end tests
│   ├── user_workflows/
│   ├── admin_workflows/
│   └── api_workflows/
├── performance/             # Performance tests
│   ├── load_tests/
│   ├── stress_tests/
│   └── benchmarks/
├── security/                # Security tests
│   ├── auth_tests/
│   ├── input_validation/
│   └── vulnerability_scans/
├── fixtures/                # Test data
├── helpers/                 # Test utilities
└── config/                  # Test configuration
```

## Unit Testing

### Framework: pytest + pytest-asyncio

#### Core Service Tests

```python
# tests/unit/services/test_code_analyzer.py
import pytest
from unittest.mock import Mock, patch
from services.code_analyzer import CodeAnalyzer, AnalysisResult
from models.code_analysis import CodeQuality, Suggestion

class TestCodeAnalyzer:
    """Test suite for CodeAnalyzer service"""
    
    @pytest.fixture
    def analyzer(self):
        """Create CodeAnalyzer instance for testing"""
        return CodeAnalyzer()
    
    @pytest.fixture
    def sample_python_code(self):
        """Sample Python code for testing"""
        return '''
def calculate_sum(a, b):
    """Calculate sum of two numbers"""
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f"Result: {result}")
'''
    
    def test_analyze_python_code_success(self, analyzer, sample_python_code):
        """Test successful Python code analysis"""
        result = analyzer.analyze(sample_python_code, "python")
        
        assert isinstance(result, AnalysisResult)
        assert result.language == "python"
        assert result.code_quality.score >= 80
        assert len(result.suggestions) >= 0
    
    def test_analyze_invalid_syntax(self, analyzer):
        """Test analysis of code with syntax errors"""
        invalid_code = "def broken_function(\n    return 'missing colon'"
        
        result = analyzer.analyze(invalid_code, "python")
        
        assert result.has_syntax_errors
        assert len(result.syntax_errors) > 0
        assert "SyntaxError" in result.syntax_errors[0].type
    
    def test_analyze_unsupported_language(self, analyzer):
        """Test analysis with unsupported language"""
        with pytest.raises(ValueError, match="Unsupported language"):
            analyzer.analyze("some code", "cobol")
    
    @pytest.mark.asyncio
    async def test_analyze_async(self, analyzer, sample_python_code):
        """Test asynchronous code analysis"""
        result = await analyzer.analyze_async(sample_python_code, "python")
        
        assert isinstance(result, AnalysisResult)
        assert result.analysis_time > 0
    
    def test_calculate_complexity(self, analyzer):
        """Test cyclomatic complexity calculation"""
        complex_code = '''
def complex_function(x):
    if x > 10:
        if x > 20:
            return "high"
        else:
            return "medium"
    elif x > 5:
        return "low"
    else:
        return "very low"
'''
        
        complexity = analyzer.calculate_complexity(complex_code, "python")
        assert complexity >= 4  # Expected complexity for this code
    
    @patch('services.code_analyzer.ollama_client')
    def test_ai_suggestions(self, mock_ollama, analyzer, sample_python_code):
        """Test AI-powered suggestions"""
        mock_ollama.generate.return_value = {
            'response': 'Consider adding type hints for better code clarity.'
        }
        
        suggestions = analyzer.get_ai_suggestions(sample_python_code, "python")
        
        assert len(suggestions) > 0
        assert any("type hints" in s.message.lower() for s in suggestions)
        mock_ollama.generate.assert_called_once()
```

#### Database Model Tests

```python
# tests/unit/models/test_document.py
import pytest
from datetime import datetime
from models.document import Document, DocumentStatus
from database.exceptions import ValidationError

class TestDocument:
    """Test suite for Document model"""
    
    def test_create_document_valid(self):
        """Test creating a valid document"""
        doc = Document(
            title="Test Document",
            content="This is test content",
            category="documentation",
            tags=["test", "example"]
        )
        
        assert doc.title == "Test Document"
        assert doc.status == DocumentStatus.PENDING
        assert isinstance(doc.created_at, datetime)
        assert doc.word_count == 4
    
    def test_create_document_invalid_title(self):
        """Test creating document with invalid title"""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            Document(title="", content="Content")
    
    def test_document_processing(self):
        """Test document processing workflow"""
        doc = Document(title="Test", content="Content")
        
        # Start processing
        doc.start_processing()
        assert doc.status == DocumentStatus.PROCESSING
        assert doc.processing_started_at is not None
        
        # Complete processing
        doc.complete_processing()
        assert doc.status == DocumentStatus.COMPLETED
        assert doc.processing_completed_at is not None
        assert doc.processing_time > 0
    
    def test_document_search_indexing(self):
        """Test document search index generation"""
        doc = Document(
            title="Python Tutorial",
            content="Learn Python programming with examples",
            tags=["python", "tutorial"]
        )
        
        search_index = doc.generate_search_index()
        
        assert "python" in search_index
        assert "tutorial" in search_index
        assert "programming" in search_index
```

#### Utility Function Tests

```python
# tests/unit/utils/test_text_processor.py
import pytest
from utils.text_processor import TextProcessor, extract_code_blocks

class TestTextProcessor:
    """Test suite for text processing utilities"""
    
    @pytest.fixture
    def processor(self):
        return TextProcessor()
    
    def test_clean_text(self, processor):
        """Test text cleaning functionality"""
        dirty_text = "  Hello\n\nWorld!  \t\r\n  "
        clean_text = processor.clean_text(dirty_text)
        
        assert clean_text == "Hello World!"
    
    def test_extract_code_blocks(self):
        """Test code block extraction from markdown"""
        markdown_text = '''
# Example

Here's some Python code:

```python
def hello():
    print("Hello, World!")
```

And some JavaScript:

```javascript
function hello() {
    console.log("Hello, World!");
}
```
'''
        
        code_blocks = extract_code_blocks(markdown_text)
        
        assert len(code_blocks) == 2
        assert code_blocks[0]['language'] == 'python'
        assert code_blocks[1]['language'] == 'javascript'
        assert 'def hello()' in code_blocks[0]['code']
        assert 'function hello()' in code_blocks[1]['code']
    
    def test_calculate_readability_score(self, processor):
        """Test readability score calculation"""
        simple_text = "This is a simple sentence."
        complex_text = "The implementation of sophisticated algorithms requires comprehensive understanding of computational complexity theory."
        
        simple_score = processor.calculate_readability(simple_text)
        complex_score = processor.calculate_readability(complex_text)
        
        assert simple_score > complex_score
        assert 0 <= simple_score <= 100
        assert 0 <= complex_score <= 100
```

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/services/test_code_analyzer.py -v

# Run tests matching pattern
pytest tests/unit/ -k "test_analyze" -v

# Run tests with markers
pytest tests/unit/ -m "not slow" -v
```

## Integration Testing

### API Integration Tests

```python
# tests/integration/api/test_code_analysis_api.py
import pytest
import asyncio
from httpx import AsyncClient
from main.main import app
from database.connection import get_test_db

@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client):
    """Get authentication headers"""
    response = await client.post("/api/v1/auth/token", json={
        "username": "test_user",
        "password": "test_password"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

class TestCodeAnalysisAPI:
    """Integration tests for Code Analysis API"""
    
    @pytest.mark.asyncio
    async def test_analyze_code_endpoint(self, client, auth_headers):
        """Test code analysis endpoint"""
        code_data = {
            "code": "def hello_world():\n    print('Hello, World!')",
            "language": "python",
            "analysis_type": "comprehensive"
        }
        
        response = await client.post(
            "/api/v1/code/analyze",
            json=code_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "analysis_id" in data
        assert "code_quality" in data
        assert data["code_quality"]["score"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_analysis_result(self, client, auth_headers):
        """Test retrieving analysis results"""
        # First, create an analysis
        code_data = {
            "code": "print('test')",
            "language": "python"
        }
        
        create_response = await client.post(
            "/api/v1/code/analyze",
            json=code_data,
            headers=auth_headers
        )
        analysis_id = create_response.json()["analysis_id"]
        
        # Then retrieve it
        response = await client.get(
            f"/api/v1/code/analysis/{analysis_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["analysis_id"] == analysis_id
        assert "results" in data
    
    @pytest.mark.asyncio
    async def test_invalid_language(self, client, auth_headers):
        """Test analysis with invalid language"""
        code_data = {
            "code": "some code",
            "language": "invalid_language"
        }
        
        response = await client.post(
            "/api/v1/code/analyze",
            json=code_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
        assert "VALIDATION_ERROR" in data["error"]["code"]
```

### Database Integration Tests

```python
# tests/integration/database/test_document_repository.py
import pytest
import asyncio
from database.repositories.document_repository import DocumentRepository
from database.connection import get_test_db
from models.document import Document, DocumentStatus

@pytest.fixture
async def db_session():
    """Create test database session"""
    async with get_test_db() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def document_repo(db_session):
    """Create document repository"""
    return DocumentRepository(db_session)

class TestDocumentRepository:
    """Integration tests for Document Repository"""
    
    @pytest.mark.asyncio
    async def test_create_document(self, document_repo):
        """Test creating a document in database"""
        doc = Document(
            title="Test Document",
            content="Test content",
            category="test"
        )
        
        created_doc = await document_repo.create(doc)
        
        assert created_doc.id is not None
        assert created_doc.title == "Test Document"
        assert created_doc.status == DocumentStatus.PENDING
    
    @pytest.mark.asyncio
    async def test_find_documents_by_category(self, document_repo):
        """Test finding documents by category"""
        # Create test documents
        doc1 = Document(title="Doc 1", content="Content 1", category="test")
        doc2 = Document(title="Doc 2", content="Content 2", category="test")
        doc3 = Document(title="Doc 3", content="Content 3", category="other")
        
        await document_repo.create(doc1)
        await document_repo.create(doc2)
        await document_repo.create(doc3)
        
        # Find by category
        test_docs = await document_repo.find_by_category("test")
        
        assert len(test_docs) == 2
        assert all(doc.category == "test" for doc in test_docs)
    
    @pytest.mark.asyncio
    async def test_search_documents(self, document_repo):
        """Test document search functionality"""
        # Create documents with searchable content
        doc1 = Document(
            title="Python Tutorial",
            content="Learn Python programming",
            tags=["python", "tutorial"]
        )
        doc2 = Document(
            title="JavaScript Guide",
            content="JavaScript programming guide",
            tags=["javascript", "guide"]
        )
        
        await document_repo.create(doc1)
        await document_repo.create(doc2)
        
        # Search for Python
        results = await document_repo.search("python")
        
        assert len(results) == 1
        assert results[0].title == "Python Tutorial"
    
    @pytest.mark.asyncio
    async def test_update_document_status(self, document_repo):
        """Test updating document status"""
        doc = Document(title="Test", content="Content")
        created_doc = await document_repo.create(doc)
        
        # Update status
        updated_doc = await document_repo.update_status(
            created_doc.id,
            DocumentStatus.PROCESSING
        )
        
        assert updated_doc.status == DocumentStatus.PROCESSING
        assert updated_doc.processing_started_at is not None
```

### Service Integration Tests

```python
# tests/integration/services/test_training_service.py
import pytest
from services.training_service import TrainingService
from services.knowledge_service import KnowledgeService
from database.connection import get_test_db

@pytest.fixture
async def training_service():
    """Create training service with dependencies"""
    db = get_test_db()
    knowledge_service = KnowledgeService(db)
    return TrainingService(db, knowledge_service)

class TestTrainingService:
    """Integration tests for Training Service"""
    
    @pytest.mark.asyncio
    async def test_create_training_session(self, training_service):
        """Test creating a complete training session"""
        session_data = {
            "session_name": "Python Basics",
            "topics": ["variables", "functions", "loops"],
            "difficulty": "beginner",
            "duration_minutes": 30
        }
        
        session = await training_service.create_session(session_data)
        
        assert session.id is not None
        assert session.name == "Python Basics"
        assert len(session.questions) > 0
        assert session.estimated_duration == 30
    
    @pytest.mark.asyncio
    async def test_complete_training_workflow(self, training_service):
        """Test complete training workflow"""
        # Create session
        session = await training_service.create_session({
            "session_name": "Test Session",
            "topics": ["functions"],
            "difficulty": "beginner"
        })
        
        # Get first question
        question = await training_service.get_next_question(session.id)
        assert question is not None
        
        # Submit answer
        answer_result = await training_service.submit_answer(
            session.id,
            question.id,
            "def example(): pass",
            time_taken=60
        )
        
        assert answer_result.score >= 0
        assert answer_result.feedback is not None
        
        # Check session progress
        progress = await training_service.get_session_progress(session.id)
        assert progress.questions_completed == 1
        assert progress.total_score >= 0
```

## End-to-End Testing

### Framework: Playwright

```python
# tests/e2e/test_user_workflows.py
import pytest
from playwright.async_api import async_playwright, Page

@pytest.fixture
async def page():
    """Create browser page for testing"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        yield page
        await browser.close()

class TestUserWorkflows:
    """End-to-end tests for user workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_code_analysis_workflow(self, page: Page):
        """Test complete code analysis workflow"""
        # Navigate to application
        await page.goto("http://localhost:3000")
        
        # Login
        await page.fill('[data-testid="username"]', "test_user")
        await page.fill('[data-testid="password"]', "test_password")
        await page.click('[data-testid="login-button"]')
        
        # Wait for dashboard
        await page.wait_for_selector('[data-testid="dashboard"]')
        
        # Navigate to code analysis
        await page.click('[data-testid="code-analysis-link"]')
        
        # Enter code
        code_input = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
        await page.fill('[data-testid="code-editor"]', code_input)
        
        # Select language
        await page.select_option('[data-testid="language-select"]', "python")
        
        # Start analysis
        await page.click('[data-testid="analyze-button"]')
        
        # Wait for results
        await page.wait_for_selector('[data-testid="analysis-results"]')
        
        # Verify results are displayed
        quality_score = await page.text_content('[data-testid="quality-score"]')
        assert quality_score is not None
        
        suggestions = await page.query_selector_all('[data-testid="suggestion-item"]')
        assert len(suggestions) >= 0
    
    @pytest.mark.asyncio
    async def test_document_upload_workflow(self, page: Page):
        """Test document upload and processing workflow"""
        await page.goto("http://localhost:3000")
        
        # Login (assuming login helper)
        await self.login(page, "test_user", "test_password")
        
        # Navigate to document upload
        await page.click('[data-testid="documents-link"]')
        await page.click('[data-testid="upload-button"]')
        
        # Upload file
        file_input = page.locator('[data-testid="file-input"]')
        await file_input.set_input_files("tests/fixtures/sample_document.pdf")
        
        # Fill metadata
        await page.fill('[data-testid="document-title"]', "Test Document")
        await page.select_option('[data-testid="category-select"]', "documentation")
        await page.fill('[data-testid="tags-input"]', "test, example")
        
        # Submit upload
        await page.click('[data-testid="submit-upload"]')
        
        # Wait for processing to complete
        await page.wait_for_selector(
            '[data-testid="processing-status"][data-status="completed"]',
            timeout=30000
        )
        
        # Verify document appears in list
        document_list = page.locator('[data-testid="document-list"]')
        await expect(document_list).to_contain_text("Test Document")
    
    @pytest.mark.asyncio
    async def test_training_session_workflow(self, page: Page):
        """Test complete training session workflow"""
        await page.goto("http://localhost:3000")
        await self.login(page, "test_user", "test_password")
        
        # Start training session
        await page.click('[data-testid="training-link"]')
        await page.click('[data-testid="start-session-button"]')
        
        # Configure session
        await page.fill('[data-testid="session-name"]', "Test Session")
        await page.check('[data-testid="topic-functions"]')
        await page.select_option('[data-testid="difficulty-select"]', "beginner")
        await page.click('[data-testid="create-session"]')
        
        # Answer questions
        for i in range(3):  # Answer 3 questions
            # Wait for question to load
            await page.wait_for_selector('[data-testid="question-content"]')
            
            # Submit answer (simplified)
            await page.fill('[data-testid="answer-input"]', "def example(): pass")
            await page.click('[data-testid="submit-answer"]')
            
            # Wait for feedback
            await page.wait_for_selector('[data-testid="answer-feedback"]')
            
            # Continue to next question (if not last)
            if i < 2:
                await page.click('[data-testid="next-question"]')
        
        # Complete session
        await page.click('[data-testid="complete-session"]')
        
        # Verify session results
        await page.wait_for_selector('[data-testid="session-results"]')
        final_score = await page.text_content('[data-testid="final-score"]')
        assert final_score is not None
    
    async def login(self, page: Page, username: str, password: str):
        """Helper method for login"""
        await page.fill('[data-testid="username"]', username)
        await page.fill('[data-testid="password"]', password)
        await page.click('[data-testid="login-button"]')
        await page.wait_for_selector('[data-testid="dashboard"]')
```

### Visual Regression Testing

```python
# tests/e2e/test_visual_regression.py
import pytest
from playwright.async_api import Page

class TestVisualRegression:
    """Visual regression tests"""
    
    @pytest.mark.asyncio
    async def test_dashboard_layout(self, page: Page):
        """Test dashboard visual layout"""
        await page.goto("http://localhost:3000")
        await self.login(page)
        
        # Take screenshot and compare
        await page.screenshot(path="tests/screenshots/dashboard.png")
        
        # Compare with baseline (using pytest-playwright)
        await expect(page).to_have_screenshot("dashboard.png")
    
    @pytest.mark.asyncio
    async def test_code_editor_appearance(self, page: Page):
        """Test code editor visual appearance"""
        await page.goto("http://localhost:3000/code-analysis")
        await self.login(page)
        
        # Fill code editor
        await page.fill('[data-testid="code-editor"]', "def hello(): pass")
        
        # Take screenshot
        await expect(page.locator('[data-testid="code-editor"]')).to_have_screenshot(
            "code-editor-with-content.png"
        )
```

## Performance Testing

### Load Testing with Locust

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between
import random
import json

class EliteCodingAssistantUser(HttpUser):
    """Simulated user for load testing"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login when user starts"""
        response = self.client.post("/api/v1/auth/token", json={
            "username": "test_user",
            "password": "test_password"
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {token}"})
    
    @task(3)
    def analyze_code(self):
        """Test code analysis endpoint"""
        code_samples = [
            "def hello(): print('world')",
            "function greet(name) { return `Hello, ${name}!`; }",
            "public class Example { public static void main(String[] args) {} }"
        ]
        
        languages = ["python", "javascript", "java"]
        
        code = random.choice(code_samples)
        language = random.choice(languages)
        
        self.client.post("/api/v1/code/analyze", json={
            "code": code,
            "language": language,
            "analysis_type": "quick"
        })
    
    @task(2)
    def search_knowledge(self):
        """Test knowledge search endpoint"""
        queries = [
            "authentication patterns",
            "database optimization",
            "error handling",
            "testing strategies"
        ]
        
        query = random.choice(queries)
        
        self.client.post("/api/v1/knowledge/search", json={
            "query": query,
            "limit": 10
        })
    
    @task(1)
    def upload_document(self):
        """Test document upload endpoint"""
        # Simulate small document upload
        files = {
            'file': ('test.txt', 'This is test content for load testing', 'text/plain')
        }
        
        data = {
            'metadata': json.dumps({
                'title': f'Load Test Document {random.randint(1, 1000)}',
                'category': 'test'
            })
        }
        
        self.client.post("/api/v1/documents/ingest", files=files, data=data)
    
    @task(1)
    def get_system_metrics(self):
        """Test system metrics endpoint"""
        self.client.get("/api/v1/admin/metrics")
```

### Benchmark Tests

```python
# tests/performance/test_benchmarks.py
import pytest
import time
import asyncio
from services.code_analyzer import CodeAnalyzer
from utils.performance import measure_time, memory_usage

class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.fixture
    def analyzer(self):
        return CodeAnalyzer()
    
    @measure_time
    def test_code_analysis_performance(self, analyzer):
        """Benchmark code analysis performance"""
        large_code = "\n".join([
            f"def function_{i}(x):\n    return x * {i}"
            for i in range(100)
        ])
        
        start_time = time.time()
        result = analyzer.analyze(large_code, "python")
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # Assert performance requirements
        assert analysis_time < 5.0  # Should complete within 5 seconds
        assert result.code_quality.score >= 0
    
    @pytest.mark.asyncio
    async def test_concurrent_analysis_performance(self, analyzer):
        """Test performance under concurrent load"""
        code_samples = [
            f"def func_{i}(): return {i}"
            for i in range(50)
        ]
        
        start_time = time.time()
        
        # Run 50 concurrent analyses
        tasks = [
            analyzer.analyze_async(code, "python")
            for code in code_samples
        ]
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All analyses should complete
        assert len(results) == 50
        assert all(r.code_quality.score >= 0 for r in results)
        
        # Should handle concurrent load efficiently
        assert total_time < 10.0  # Should complete within 10 seconds
    
    @memory_usage
    def test_memory_usage_analysis(self, analyzer):
        """Test memory usage during analysis"""
        # Generate large code sample
        large_code = "\n".join([
            f"class Class_{i}:\n    def method_{j}(self):\n        return {i * j}"
            for i in range(20)
            for j in range(10)
        ])
        
        # Perform analysis
        result = analyzer.analyze(large_code, "python")
        
        # Memory usage should be reasonable
        # (memory_usage decorator will track this)
        assert result is not None
```

## Security Testing

### Authentication & Authorization Tests

```python
# tests/security/test_auth_security.py
import pytest
from httpx import AsyncClient
from main.main import app

class TestAuthSecurity:
    """Security tests for authentication and authorization"""
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self):
        """Test that protected endpoints require authentication"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Try to access protected endpoint without token
            response = await client.get("/api/v1/admin/metrics")
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """Test handling of invalid tokens"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            headers = {"Authorization": "Bearer invalid_token"}
            response = await client.get("/api/v1/admin/metrics", headers=headers)
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_token_expiration(self):
        """Test token expiration handling"""
        # This would require mocking time or using expired tokens
        pass
    
    @pytest.mark.asyncio
    async def test_role_based_access(self):
        """Test role-based access control"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Get user token (non-admin)
            user_response = await client.post("/api/v1/auth/token", json={
                "username": "regular_user",
                "password": "password"
            })
            user_token = user_response.json()["access_token"]
            
            # Try to access admin endpoint
            headers = {"Authorization": f"Bearer {user_token}"}
            response = await client.get("/api/v1/admin/users", headers=headers)
            assert response.status_code == 403
```

### Input Validation Tests

```python
# tests/security/test_input_validation.py
import pytest
from httpx import AsyncClient
from main.main import app

class TestInputValidation:
    """Security tests for input validation"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Try SQL injection in search
            malicious_query = "'; DROP TABLE documents; --"
            
            response = await client.post("/api/v1/knowledge/search", json={
                "query": malicious_query
            })
            
            # Should not cause server error
            assert response.status_code in [200, 400, 422]
    
    @pytest.mark.asyncio
    async def test_xss_prevention(self):
        """Test XSS prevention in user inputs"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            xss_payload = "<script>alert('xss')</script>"
            
            response = await client.post("/api/v1/feedback", json={
                "type": "suggestion",
                "title": xss_payload,
                "description": "Test description"
            })
            
            # Should sanitize input
            if response.status_code == 200:
                # Verify XSS payload is sanitized in response
                assert "<script>" not in response.text
    
    @pytest.mark.asyncio
    async def test_file_upload_validation(self):
        """Test file upload security"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Try to upload malicious file
            malicious_content = b"<?php system($_GET['cmd']); ?>"
            
            files = {
                'file': ('malicious.php', malicious_content, 'application/x-php')
            }
            
            response = await client.post("/api/v1/documents/ingest", files=files)
            
            # Should reject malicious file types
            assert response.status_code in [400, 422]
```

### Vulnerability Scanning

```python
# tests/security/test_vulnerability_scan.py
import pytest
import requests
from security.scanners import SecurityScanner

class TestVulnerabilityScanning:
    """Automated vulnerability scanning tests"""
    
    def test_dependency_vulnerabilities(self):
        """Test for known vulnerabilities in dependencies"""
        scanner = SecurityScanner()
        vulnerabilities = scanner.scan_dependencies()
        
        # Should have no high or critical vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.severity == 'critical']
        high_vulns = [v for v in vulnerabilities if v.severity == 'high']
        
        assert len(critical_vulns) == 0, f"Critical vulnerabilities found: {critical_vulns}"
        assert len(high_vulns) == 0, f"High severity vulnerabilities found: {high_vulns}"
    
    def test_ssl_configuration(self):
        """Test SSL/TLS configuration"""
        # This would test SSL configuration in production
        # For local testing, we might skip or mock
        pass
    
    def test_security_headers(self):
        """Test security headers are present"""
        response = requests.get("http://localhost:8000")
        
        # Check for security headers
        assert 'X-Content-Type-Options' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers
        
        # Verify header values
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['X-Frame-Options'] == 'DENY'
```

## Test Configuration

### pytest.ini

```ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    -q
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
testpaths = tests
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    security: marks tests as security tests
    performance: marks tests as performance tests
    unit: marks tests as unit tests
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
```

### Test Environment Configuration

```python
# tests/config/test_settings.py
import os
from pydantic import BaseSettings

class TestSettings(BaseSettings):
    """Test environment configuration"""
    
    # Database
    TEST_DATABASE_URL: str = "postgresql://test:test@localhost:5432/elite_test"
    
    # Redis
    TEST_REDIS_URL: str = "redis://localhost:6379/1"
    
    # API
    TEST_API_BASE_URL: str = "http://localhost:8000"
    
    # Authentication
    TEST_SECRET_KEY: str = "test-secret-key"
    TEST_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    TEST_OLLAMA_URL: str = "http://localhost:11434"
    
    # File Storage
    TEST_UPLOAD_DIR: str = "/tmp/elite_test_uploads"
    
    # Performance
    TEST_MAX_ANALYSIS_TIME: float = 5.0
    TEST_MAX_MEMORY_USAGE_MB: int = 512
    
    class Config:
        env_file = ".env.test"

test_settings = TestSettings()
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_USER: test
          POSTGRES_DB: elite_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
      env:
        TEST_DATABASE_URL: postgresql://test:test@localhost:5432/elite_test
        TEST_REDIS_URL: redis://localhost:6379/1
    
    - name: Run security tests
      run: |
        pytest tests/security/ -v
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
  
  e2e-tests:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install playwright pytest-playwright
        playwright install
    
    - name: Start application
      run: |
        python main/main.py &
        sleep 10
      env:
        ENVIRONMENT: test
    
    - name: Run E2E tests
      run: |
        pytest tests/e2e/ -v
    
    - name: Upload test artifacts
      uses: actions/upload-artifact@v3
      if: failure()
      with:
        name: test-results
        path: |
          tests/screenshots/
          tests/videos/
```

## Test Data Management

### Fixtures and Test Data

```python
# tests/fixtures/data_factory.py
from factory import Factory, Faker, SubFactory
from models.document import Document
from models.user import User
from models.training_session import TrainingSession

class UserFactory(Factory):
    """Factory for creating test users"""
    
    class Meta:
        model = User
    
    username = Faker('user_name')
    email = Faker('email')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_active = True
    role = 'developer'

class DocumentFactory(Factory):
    """Factory for creating test documents"""
    
    class Meta:
        model = Document
    
    title = Faker('sentence', nb_words=4)
    content = Faker('text', max_nb_chars=1000)
    category = Faker('random_element', elements=['documentation', 'tutorial', 'reference'])
    tags = Faker('words', nb=3)
    author = SubFactory(UserFactory)

class TrainingSessionFactory(Factory):
    """Factory for creating test training sessions"""
    
    class Meta:
        model = TrainingSession
    
    name = Faker('sentence', nb_words=3)
    difficulty = Faker('random_element', elements=['beginner', 'intermediate', 'advanced'])
    duration_minutes = Faker('random_int', min=15, max=120)
    user = SubFactory(UserFactory)
```

### Database Seeding

```python
# tests/helpers/database_seeder.py
import asyncio
from database.connection import get_test_db
from tests.fixtures.data_factory import UserFactory, DocumentFactory

class DatabaseSeeder:
    """Seed test database with sample data"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def seed_users(self, count: int = 10):
        """Create test users"""
        users = [UserFactory() for _ in range(count)]
        
        for user in users:
            self.db.add(user)
        
        await self.db.commit()
        return users
    
    async def seed_documents(self, count: int = 20):
        """Create test documents"""
        documents = [DocumentFactory() for _ in range(count)]
        
        for doc in documents:
            self.db.add(doc)
        
        await self.db.commit()
        return documents
    
    async def seed_all(self):
        """Seed all test data"""
        users = await self.seed_users()
        documents = await self.seed_documents()
        
        return {
            'users': users,
            'documents': documents
        }
```

## Test Reporting

### Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Generate XML coverage report for CI
pytest --cov=src --cov-report=xml

# Show missing lines
pytest --cov=src --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

### Test Results Dashboard

```python
# scripts/generate_test_report.py
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

def generate_test_report():
    """Generate comprehensive test report"""
    
    # Parse pytest results
    junit_xml = Path('test-results.xml')
    coverage_xml = Path('coverage.xml')
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {},
        'coverage': {},
        'test_results': {}
    }
    
    # Parse JUnit XML
    if junit_xml.exists():
        tree = ET.parse(junit_xml)
        root = tree.getroot()
        
        report['summary'] = {
            'total_tests': int(root.attrib.get('tests', 0)),
            'failures': int(root.attrib.get('failures', 0)),
            'errors': int(root.attrib.get('errors', 0)),
            'skipped': int(root.attrib.get('skipped', 0)),
            'time': float(root.attrib.get('time', 0))
        }
    
    # Parse coverage XML
    if coverage_xml.exists():
        tree = ET.parse(coverage_xml)
        root = tree.getroot()
        
        coverage_elem = root.find('coverage')
        if coverage_elem is not None:
            report['coverage'] = {
                'line_rate': float(coverage_elem.attrib.get('line-rate', 0)) * 100,
                'branch_rate': float(coverage_elem.attrib.get('branch-rate', 0)) * 100
            }
    
    # Save report
    with open('test-report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Test report generated: {report['summary']}")
    print(f"Coverage: {report['coverage'].get('line_rate', 0):.1f}%")

if __name__ == '__main__':
    generate_test_report()
```

## Best Practices

### Test Organization

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **One Assertion Per Test**: Focus on single behavior
3. **Descriptive Test Names**: Clearly describe what is being tested
4. **Use Fixtures**: Share setup code efficiently
5. **Mock External Dependencies**: Keep tests isolated

### Test Maintenance

1. **Regular Review**: Update tests when code changes
2. **Remove Obsolete Tests**: Clean up unused tests
3. **Refactor Test Code**: Apply same quality standards as production code
4. **Monitor Test Performance**: Keep tests fast
5. **Update Test Data**: Keep fixtures relevant

### Quality Gates

1. **Minimum Coverage**: 80% line coverage
2. **No Failing Tests**: All tests must pass
3. **Performance Thresholds**: Tests complete within time limits
4. **Security Scans**: No critical vulnerabilities
5. **Code Quality**: Tests follow coding standards

---

**Testing Framework**: pytest, Playwright, Locust  
**Last Updated**: December 19, 2024  
**Coverage Target**: 80%  
**Test Automation**: GitHub Actions