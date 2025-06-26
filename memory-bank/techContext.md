# Technical Context - Enhanced Elite Coding Assistant

## Technology Stack

### Core Technologies

#### Backend Framework
- **Pydantic AI**: Primary agent framework for intelligent orchestration
- **FastAPI**: Web framework for REST APIs and real-time endpoints
- **Python 3.11+**: Core programming language with modern async support
- **AsyncIO**: Asynchronous programming for concurrent operations
- **WebSockets**: Real-time bidirectional communication protocol
- **Starlette**: ASGI framework powering FastAPI's WebSocket support

#### AI and Machine Learning
- **Ollama**: Local LLM inference engine
- **Hugging Face Transformers**: Pre-trained models and tokenizers
- **MLflow**: Experiment tracking, model registry, and deployment
- **Sentence Transformers**: Embedding generation for semantic search

#### Data Management
- **Supabase**: PostgreSQL database with real-time capabilities
- **Redis**: Caching, session management, and pub/sub for real-time features
- **AsyncPG**: Async PostgreSQL driver
- **Pydantic**: Data validation and serialization
- **Redis Streams**: Time-series data structure for real-time event processing
- **Redis PubSub**: Publisher-subscriber pattern for real-time messaging

#### Document Processing (Phase 5)
- **PyPDF2**: PDF document parsing and extraction
- **python-docx**: Microsoft Word document processing
- **BeautifulSoup4**: HTML parsing and web scraping
- **Markdown**: Markdown document processing

#### Development Tools
- **Pytest**: Testing framework with async support
- **Black**: Code formatting
- **Mypy**: Static type checking
- **Pre-commit**: Git hooks for code quality

### Architecture Patterns

#### Microservices Design
```python
# Service architecture pattern
class BaseService:
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.event_bus = EventBus()
        self.metrics = MetricsCollector()
        
    async def start(self):
        await self.initialize()
        await self.register_handlers()
```

#### Event-Driven Communication
```python
# Event system for inter-service communication
class EventBus:
    def __init__(self):
        self.handlers = defaultdict(list)
        
    async def publish(self, event: Event):
        for handler in self.handlers[event.type]:
            await handler(event)
```

#### Plugin System
```python
# Extensible plugin architecture
class DocumentProcessor(ABC):
    @abstractmethod
    def can_process(self, file_path: str) -> bool:
        pass
        
    @abstractmethod
    async def process(self, file_path: str) -> ProcessedDocument:
        pass
```

### Development Environment

#### Local Development Setup
```bash
# Python environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
supabase start
psql -f supabase_learning_schema.sql

# Local LLM setup
ollama pull llama2
ollama serve
```

#### Configuration Management
```python
# Pydantic-based configuration
class SystemConfig(BaseModel):
    database_url: str
    ollama_base_url: str = "http://localhost:11434"
    redis_url: str = "redis://localhost:6379"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

### Technical Constraints

#### Performance Requirements
- **Response Time**: < 200ms for API endpoints (95th percentile)
- **Throughput**: Support 100+ concurrent users
- **Memory Usage**: < 2GB under normal load
- **Startup Time**: < 30 seconds for full system initialization

#### Scalability Considerations
- Horizontal scaling through microservices
- Database connection pooling
- Redis caching for frequently accessed data
- Async processing for I/O-bound operations

#### Security Requirements
- Input validation using Pydantic models
- SQL injection prevention through parameterized queries
- Rate limiting on public endpoints
- Secure credential management

### Dependencies

#### Core Dependencies
```python
# requirements.txt (core)
fastapi>=0.104.0
pydantic>=2.5.0
pydantic-ai>=0.0.13
ollama>=0.1.7
supabase>=2.0.0
asyncpg>=0.29.0
redis>=5.0.0
psutil>=5.9.0
```

#### Phase 5 Specific Dependencies
```python
# Document processing
PyPDF2>=3.0.1
python-docx>=1.1.0
beautifulsoup4>=4.12.0
markdown>=3.5.0

# ML and AI
transformers>=4.35.0
sentence-transformers>=2.2.2
mlflow>=2.8.0
torch>=2.1.0

# Web framework
streamlit>=1.28.0  # For interactive training interface
websockets>=12.0   # For real-time communication
```

#### Development Dependencies
```python
# Testing and quality
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.9.0
mypy>=1.6.0
pre-commit>=3.5.0
```

### Integration Points

#### External Services
- **Ollama API**: Local LLM inference
- **Supabase**: Database and real-time subscriptions
- **Redis**: Caching and session storage
- **MLflow Tracking Server**: Experiment management

#### Internal APIs
```python
# Service communication patterns
class ServiceRegistry:
    def __init__(self):
        self.services = {}
        
    async def register_service(self, name: str, service: BaseService):
        self.services[name] = service
        await service.start()
        
    async def get_service(self, name: str) -> BaseService:
        return self.services.get(name)
```

### Deployment Architecture

#### Local Development
```yaml
# docker-compose.yml structure
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  supabase:
    # Supabase local development setup
```

#### Production Considerations
- Container orchestration (Docker/Kubernetes)
- Load balancing for API endpoints
- Database replication and backup
- Monitoring and logging infrastructure

### Phase 5 Technical Implementation

#### Document Ingestion System
```python
# Technical architecture for document processing
class DocumentIngestionService:
    def __init__(self):
        self.processors = ProcessorRegistry()
        self.validators = ValidatorRegistry()
        self.storage = DocumentStorage()
        
    async def ingest_document(self, file_path: str) -> IngestionResult:
        processor = self.processors.get_processor(file_path)
        document = await processor.process(file_path)
        
        validation_result = await self.validators.validate(document)
        if validation_result.is_valid:
            await self.storage.store(document)
            
        return IngestionResult(document, validation_result)
```

#### Interactive Training Interface
```python
# Streamlit-based training interface
class TrainingInterface:
    def __init__(self):
        self.session_manager = SessionManager()
        self.feedback_collector = FeedbackCollector()
        
    async def create_training_session(self, user_id: str) -> TrainingSession:
        session = await self.session_manager.create_session(user_id)
        return session
        
    async def process_interaction(self, session_id: str, interaction: Interaction):
        session = await self.session_manager.get_session(session_id)
        response = await session.process_interaction(interaction)
        await self.feedback_collector.collect_feedback(session_id, response)
        return response
```

#### Knowledge Validation
```python
# Multi-layer validation system
class KnowledgeValidator:
    def __init__(self):
        self.accuracy_checker = AccuracyChecker()
        self.conflict_detector = ConflictDetector()
        self.quality_scorer = QualityScorer()
        
    async def validate_knowledge(self, knowledge: Knowledge) -> ValidationResult:
        accuracy_score = await self.accuracy_checker.check(knowledge)
        conflicts = await self.conflict_detector.detect(knowledge)
        quality_score = await self.quality_scorer.score(knowledge)
        
        return ValidationResult(
            accuracy_score=accuracy_score,
            conflicts=conflicts,
            quality_score=quality_score
        )
```

### Monitoring and Observability

#### Logging Configuration
```python
# Structured logging setup
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

#### Metrics Collection
```python
# Performance metrics tracking
class MetricsCollector:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = defaultdict(list)
        self.gauges = defaultdict(float)
        
    async def increment_counter(self, name: str, value: int = 1):
        self.counters[name] += value
        
    async def record_timer(self, name: str, duration: float):
        self.timers[name].append(duration)
        
    async def set_gauge(self, name: str, value: float):
        self.gauges[name] = value
```

### Testing Strategy

#### Unit Testing
```python
# Async test patterns
@pytest.mark.asyncio
async def test_document_processing():
    processor = PDFProcessor()
    result = await processor.process("test.pdf")
    assert result.status == "success"
    assert len(result.content) > 0
```

#### Integration Testing
```python
# Service integration tests
@pytest.mark.asyncio
async def test_full_ingestion_pipeline():
    async with TestClient() as client:
        response = await client.post("/ingest", files={"file": test_file})
        assert response.status_code == 200
        
        # Verify document was processed and stored
        stored_doc = await client.get(f"/documents/{response.json()['id']}")
        assert stored_doc.status_code == 200
```

### Future Technical Considerations

#### Scalability Roadmap
- Kubernetes deployment for container orchestration
- Microservices decomposition for independent scaling
- Event streaming with Apache Kafka
- Distributed caching with Redis Cluster

#### Technology Evolution
- Migration to newer LLM frameworks as they mature
- Integration with cloud-native AI services
- Advanced monitoring with OpenTelemetry
- GraphQL API layer for flexible data access

### Known Technical Limitations

#### Current Constraints
- Single-node Ollama deployment limits concurrent LLM requests
- In-memory caching doesn't persist across restarts
- File upload size limited by available memory
- No built-in backup/restore for local data

#### Mitigation Strategies
- Implement request queuing for LLM operations
- Add persistent caching layer with Redis
- Stream large file uploads to disk
- Regular automated backups to cloud storage