# Elite Coding Assistant - API Documentation

## Overview

The Elite Coding Assistant provides a comprehensive REST API for all system functionality, including code analysis, training, knowledge management, and system administration.

**Base URL**: `http://localhost:8000/api/v1`  
**Authentication**: Bearer Token  
**Content Type**: `application/json`

## Authentication

### Bearer Token Authentication

```http
Authorization: Bearer <your-token>
```

### Obtain Access Token

```http
POST /api/v1/auth/token
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Core API Endpoints

### Health Check

#### GET /health

Check system health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ollama": "healthy"
  }
}
```

### Code Analysis

#### POST /api/v1/code/analyze

Analyze code for patterns, quality, and suggestions.

**Request:**
```json
{
  "code": "def hello_world():\n    print('Hello, World!')",
  "language": "python",
  "analysis_type": "comprehensive",
  "options": {
    "include_suggestions": true,
    "check_security": true,
    "performance_analysis": true
  }
}
```

**Response:**
```json
{
  "analysis_id": "analysis_123",
  "code_quality": {
    "score": 85,
    "grade": "B+",
    "metrics": {
      "complexity": 2,
      "maintainability": 90,
      "readability": 88
    }
  },
  "suggestions": [
    {
      "type": "improvement",
      "line": 2,
      "message": "Consider adding a docstring",
      "severity": "low"
    }
  ],
  "security_issues": [],
  "performance_insights": [
    {
      "type": "optimization",
      "description": "Function is well-optimized for its purpose"
    }
  ]
}
```

#### GET /api/v1/code/analysis/{analysis_id}

Retrieve analysis results by ID.

**Response:**
```json
{
  "analysis_id": "analysis_123",
  "status": "completed",
  "created_at": "2024-12-19T10:30:00Z",
  "completed_at": "2024-12-19T10:30:05Z",
  "results": {
    // Analysis results object
  }
}
```

### Document Ingestion

#### POST /api/v1/documents/ingest

Ingest documents for knowledge base.

**Request (Multipart Form):**
```http
POST /api/v1/documents/ingest
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="file"; filename="document.pdf"
Content-Type: application/pdf

[Binary file content]
--boundary
Content-Disposition: form-data; name="metadata"

{
  "title": "API Documentation",
  "category": "documentation",
  "tags": ["api", "reference"]
}
--boundary--
```

**Response:**
```json
{
  "document_id": "doc_456",
  "status": "processing",
  "filename": "document.pdf",
  "size": 1024000,
  "pages": 25,
  "estimated_processing_time": 120
}
```

#### GET /api/v1/documents/{document_id}/status

Check document processing status.

**Response:**
```json
{
  "document_id": "doc_456",
  "status": "completed",
  "progress": 100,
  "extracted_content": {
    "text_length": 15000,
    "sections": 8,
    "code_blocks": 12
  },
  "processing_time": 95
}
```

#### GET /api/v1/documents

List all documents with filtering.

**Query Parameters:**
- `category`: Filter by category
- `tags`: Filter by tags (comma-separated)
- `status`: Filter by processing status
- `limit`: Number of results (default: 20)
- `offset`: Pagination offset (default: 0)

**Response:**
```json
{
  "documents": [
    {
      "document_id": "doc_456",
      "title": "API Documentation",
      "category": "documentation",
      "tags": ["api", "reference"],
      "status": "completed",
      "created_at": "2024-12-19T10:30:00Z",
      "size": 1024000
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### Knowledge Management

#### POST /api/v1/knowledge/search

Search knowledge base.

**Request:**
```json
{
  "query": "How to implement authentication?",
  "filters": {
    "categories": ["documentation", "tutorials"],
    "tags": ["auth", "security"]
  },
  "limit": 10,
  "include_snippets": true
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc_789",
      "title": "Authentication Guide",
      "relevance_score": 0.95,
      "snippet": "To implement authentication, you need to...",
      "section": "Getting Started",
      "page": 3
    }
  ],
  "total_results": 1,
  "query_time": 0.05
}
```

#### POST /api/v1/knowledge/validate

Validate knowledge against code patterns.

**Request:**
```json
{
  "code_snippet": "app.use(express.json())",
  "language": "javascript",
  "context": "Express.js middleware setup"
}
```

**Response:**
```json
{
  "validation_id": "val_101",
  "is_valid": true,
  "confidence": 0.92,
  "matches": [
    {
      "document_id": "doc_express",
      "section": "Middleware Configuration",
      "similarity": 0.88
    }
  ],
  "suggestions": [
    "Consider adding error handling middleware"
  ]
}
```

### Training Interface

#### POST /api/v1/training/sessions

Create a new training session.

**Request:**
```json
{
  "session_name": "Advanced Python Patterns",
  "topics": ["decorators", "metaclasses", "async"],
  "difficulty": "advanced",
  "duration_minutes": 60
}
```

**Response:**
```json
{
  "session_id": "session_202",
  "status": "created",
  "estimated_questions": 15,
  "topics_covered": ["decorators", "metaclasses", "async"],
  "start_url": "/training/session_202"
}
```

#### GET /api/v1/training/sessions/{session_id}/question

Get next question in training session.

**Response:**
```json
{
  "question_id": "q_501",
  "type": "code_completion",
  "question": "Complete the decorator implementation:",
  "code_template": "def my_decorator(func):\n    # Your code here",
  "options": [
    "def wrapper(*args, **kwargs):",
    "return func(*args, **kwargs)",
    "return wrapper"
  ],
  "difficulty": "medium",
  "time_limit": 300
}
```

#### POST /api/v1/training/sessions/{session_id}/answer

Submit answer to training question.

**Request:**
```json
{
  "question_id": "q_501",
  "answer": "def wrapper(*args, **kwargs):\n    return func(*args, **kwargs)\nreturn wrapper",
  "time_taken": 120
}
```

**Response:**
```json
{
  "correct": true,
  "score": 85,
  "explanation": "Excellent! Your decorator implementation is correct.",
  "feedback": {
    "strengths": ["Proper wrapper function", "Correct return statement"],
    "improvements": ["Consider adding functools.wraps for better debugging"]
  },
  "next_question_available": true
}
```

### Feedback System

#### POST /api/v1/feedback

Submit user feedback.

**Request:**
```json
{
  "type": "suggestion",
  "category": "feature_request",
  "title": "Add syntax highlighting",
  "description": "It would be great to have syntax highlighting in code examples",
  "priority": "medium",
  "context": {
    "page": "/training/session_202",
    "user_agent": "Mozilla/5.0..."
  }
}
```

**Response:**
```json
{
  "feedback_id": "fb_303",
  "status": "received",
  "ticket_number": "ELITE-1234",
  "estimated_review_time": "2-3 business days"
}
```

#### GET /api/v1/feedback/{feedback_id}

Get feedback status and response.

**Response:**
```json
{
  "feedback_id": "fb_303",
  "status": "in_review",
  "submitted_at": "2024-12-19T10:30:00Z",
  "last_updated": "2024-12-19T14:20:00Z",
  "response": {
    "message": "Thank you for your suggestion. We're evaluating this feature.",
    "estimated_implementation": "Q1 2025"
  }
}
```

### Learning Materials

#### GET /api/v1/materials

Get available learning materials.

**Query Parameters:**
- `category`: Filter by category
- `difficulty`: Filter by difficulty level
- `language`: Filter by programming language
- `format`: Filter by material format (video, text, interactive)

**Response:**
```json
{
  "materials": [
    {
      "material_id": "mat_404",
      "title": "Python Decorators Deep Dive",
      "category": "advanced_concepts",
      "difficulty": "advanced",
      "language": "python",
      "format": "interactive",
      "duration_minutes": 45,
      "rating": 4.8,
      "completion_rate": 0.73
    }
  ],
  "total": 1
}
```

#### GET /api/v1/materials/{material_id}

Get specific learning material content.

**Response:**
```json
{
  "material_id": "mat_404",
  "title": "Python Decorators Deep Dive",
  "content": {
    "sections": [
      {
        "title": "Introduction to Decorators",
        "content": "Decorators are a powerful feature...",
        "code_examples": [
          {
            "title": "Basic Decorator",
            "code": "def my_decorator(func):\n    def wrapper():\n        print('Before')\n        func()\n        print('After')\n    return wrapper"
          }
        ]
      }
    ]
  },
  "prerequisites": ["Functions", "Closures"],
  "learning_objectives": [
    "Understand decorator syntax",
    "Implement custom decorators"
  ]
}
```

## System Administration

### System Metrics

#### GET /api/v1/admin/metrics

Get system performance metrics.

**Headers:**
```http
Authorization: Bearer <admin-token>
```

**Response:**
```json
{
  "system": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1,
    "uptime_seconds": 86400
  },
  "application": {
    "active_sessions": 42,
    "requests_per_minute": 150,
    "average_response_time": 0.25,
    "error_rate": 0.02
  },
  "database": {
    "connections": 15,
    "query_time_avg": 0.05,
    "cache_hit_rate": 0.92
  }
}
```

### User Management

#### GET /api/v1/admin/users

List system users.

**Response:**
```json
{
  "users": [
    {
      "user_id": "user_505",
      "username": "john_doe",
      "email": "john@example.com",
      "role": "developer",
      "last_login": "2024-12-19T09:15:00Z",
      "status": "active"
    }
  ],
  "total": 1
}
```

#### POST /api/v1/admin/users

Create new user.

**Request:**
```json
{
  "username": "jane_smith",
  "email": "jane@example.com",
  "password": "secure_password",
  "role": "developer",
  "permissions": ["code_analysis", "training_access"]
}
```

**Response:**
```json
{
  "user_id": "user_506",
  "username": "jane_smith",
  "status": "created",
  "activation_required": true
}
```

## WebSocket API

### Real-time Code Analysis

**Connection:** `ws://localhost:8000/ws/code-analysis`

**Authentication:**
```json
{
  "type": "auth",
  "token": "your-bearer-token"
}
```

**Send Code for Analysis:**
```json
{
  "type": "analyze",
  "data": {
    "code": "function example() { return 'hello'; }",
    "language": "javascript",
    "real_time": true
  }
}
```

**Receive Analysis Results:**
```json
{
  "type": "analysis_result",
  "data": {
    "suggestions": [
      {
        "line": 1,
        "message": "Consider using const for immutable values",
        "type": "style"
      }
    ],
    "errors": [],
    "warnings": []
  }
}
```

### Training Session Updates

**Connection:** `ws://localhost:8000/ws/training/{session_id}`

**Receive Progress Updates:**
```json
{
  "type": "progress_update",
  "data": {
    "questions_completed": 5,
    "total_questions": 15,
    "current_score": 85,
    "time_remaining": 1800
  }
}
```

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "language",
      "issue": "Unsupported language: 'cobol'"
    },
    "timestamp": "2024-12-19T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `PROCESSING_ERROR` | Error during processing |
| `SERVICE_UNAVAILABLE` | External service unavailable |
| `INTERNAL_ERROR` | Internal server error |

## Rate Limiting

### Default Limits

- **General API**: 1000 requests per hour per user
- **Code Analysis**: 100 requests per hour per user
- **Document Ingestion**: 50 requests per hour per user
- **Training Sessions**: 10 concurrent sessions per user

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640000000
X-RateLimit-Window: 3600
```

## SDK Examples

### Python SDK

```python
from elite_coding_assistant import EliteClient

# Initialize client
client = EliteClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Analyze code
result = client.code.analyze(
    code="def hello(): print('world')",
    language="python"
)

print(f"Quality Score: {result.quality_score}")
for suggestion in result.suggestions:
    print(f"Line {suggestion.line}: {suggestion.message}")

# Search knowledge base
results = client.knowledge.search(
    query="authentication patterns",
    limit=5
)

for result in results:
    print(f"{result.title}: {result.snippet}")
```

### JavaScript SDK

```javascript
import { EliteClient } from '@elite/coding-assistant-sdk';

// Initialize client
const client = new EliteClient({
  baseUrl: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Analyze code
const analysis = await client.code.analyze({
  code: 'function hello() { console.log("world"); }',
  language: 'javascript'
});

console.log(`Quality Score: ${analysis.qualityScore}`);
analysis.suggestions.forEach(suggestion => {
  console.log(`Line ${suggestion.line}: ${suggestion.message}`);
});

// Real-time analysis via WebSocket
const ws = client.code.createRealtimeAnalyzer();
ws.on('analysis', (result) => {
  console.log('Real-time analysis:', result);
});

ws.analyze({
  code: 'const x = 1;',
  language: 'javascript'
});
```

## Changelog

### v1.0.0 (2024-12-19)
- Initial API release
- Core code analysis endpoints
- Document ingestion system
- Training interface API
- Knowledge management endpoints
- WebSocket support for real-time features

---

**API Version**: 1.0.0  
**Last Updated**: December 19, 2024  
**Support**: api-support@elite-coding-assistant.com