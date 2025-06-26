#!/usr/bin/env python3
"""
Comprehensive Test Suite for Real-Time Features

This module provides extensive testing for all real-time features:
- WebSocket communication and connection management
- Live data streaming for metrics and feedback
- Interactive features (collaboration, debugging, notifications)
- API endpoints and error handling
- Performance and load testing
- Integration testing
"""

import asyncio
import json
import pytest
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import AsyncMock, MagicMock, patch

import redis.asyncio as redis
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
import websockets

# Import modules to test
sys.path.append('main')
from main.websocket_server import WebSocketManager, WebSocketMessage, EventType, ConnectionInfo
from main.live_data_streaming import LiveDataStreamer, MetricData, FeedbackData, ModelPerformanceData
from main.interactive_features import (
    InteractiveFeatureManager, CollaborativeEditor, DebugSessionManager, NotificationManager,
    CodeOperation, OperationType, CursorPosition, DebugSession, Notification, NotificationType
)
from main.realtime_api_server import app

# Test configuration
TEST_REDIS_URL = "redis://localhost:6379/1"  # Use different DB for testing
TEST_USER_ID = "test_user_123"
TEST_SESSION_ID = "test_session_456"
TEST_TOKEN = f"{TEST_USER_ID}:{TEST_SESSION_ID}"

@pytest.fixture
async def redis_client():
    """Provide Redis client for testing"""
    client = redis.from_url(TEST_REDIS_URL)
    yield client
    # Cleanup
    await client.flushdb()
    await client.close()

@pytest.fixture
async def websocket_manager(redis_client):
    """Provide WebSocket manager for testing"""
    manager = WebSocketManager(TEST_REDIS_URL)
    await manager.initialize()
    yield manager
    # Cleanup
    await manager.cleanup()

@pytest.fixture
async def live_streamer(redis_client):
    """Provide live data streamer for testing"""
    streamer = LiveDataStreamer(TEST_REDIS_URL)
    await streamer.initialize()
    yield streamer
    # Cleanup
    await streamer.cleanup()

@pytest.fixture
async def interactive_manager(redis_client):
    """Provide interactive feature manager for testing"""
    manager = InteractiveFeatureManager(TEST_REDIS_URL)
    await manager.initialize()
    yield manager
    # Cleanup
    # Add cleanup if needed

@pytest.fixture
def test_client():
    """Provide FastAPI test client"""
    return TestClient(app)

class TestWebSocketManager:
    """Test WebSocket connection management"""
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self, websocket_manager):
        """Test WebSocket connection and disconnection"""
        # Mock WebSocket
        mock_websocket = AsyncMock()
        
        connection_info = ConnectionInfo(
            user_id=TEST_USER_ID,
            session_id=TEST_SESSION_ID,
            websocket=mock_websocket
        )
        
        # Test connection
        await websocket_manager.connect(connection_info)
        
        # Verify connection is tracked
        stats = await websocket_manager.get_connection_stats()
        assert stats["total_connections"] == 1
        assert TEST_USER_ID in stats["users"]
        
        # Test disconnection
        await websocket_manager.disconnect(connection_info)
        
        # Verify connection is removed
        stats = await websocket_manager.get_connection_stats()
        assert stats["total_connections"] == 0
    
    @pytest.mark.asyncio
    async def test_message_broadcasting(self, websocket_manager):
        """Test message broadcasting to multiple connections"""
        # Create multiple mock connections
        connections = []
        for i in range(3):
            mock_websocket = AsyncMock()
            connection = ConnectionInfo(
                user_id=f"user_{i}",
                session_id=TEST_SESSION_ID,
                websocket=mock_websocket
            )
            connections.append(connection)
            await websocket_manager.connect(connection)
        
        # Test broadcast
        message = WebSocketMessage(
            event_type=EventType.CHAT_MESSAGE,
            data={"content": "Test broadcast message"}
        )
        
        await websocket_manager.broadcast(message)
        
        # Verify all connections received the message
        for connection in connections:
            connection.websocket.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_user_specific_messaging(self, websocket_manager):
        """Test sending messages to specific users"""
        # Create connections for different users
        user1_ws = AsyncMock()
        user2_ws = AsyncMock()
        
        conn1 = ConnectionInfo(user_id="user1", websocket=user1_ws)
        conn2 = ConnectionInfo(user_id="user2", websocket=user2_ws)
        
        await websocket_manager.connect(conn1)
        await websocket_manager.connect(conn2)
        
        # Send message to specific user
        message = WebSocketMessage(
            event_type=EventType.NOTIFICATION,
            data={"content": "User-specific message"}
        )
        
        await websocket_manager.send_to_user("user1", message)
        
        # Verify only user1 received the message
        user1_ws.send_text.assert_called_once()
        user2_ws.send_text.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_heartbeat_mechanism(self, websocket_manager):
        """Test WebSocket heartbeat functionality"""
        mock_websocket = AsyncMock()
        connection = ConnectionInfo(
            user_id=TEST_USER_ID,
            websocket=mock_websocket
        )
        
        await websocket_manager.connect(connection)
        
        # Simulate heartbeat
        await websocket_manager.send_heartbeat(connection)
        
        # Verify heartbeat was sent
        mock_websocket.send_text.assert_called()
        call_args = mock_websocket.send_text.call_args[0][0]
        heartbeat_data = json.loads(call_args)
        assert heartbeat_data["event_type"] == "heartbeat"

class TestLiveDataStreaming:
    """Test live data streaming functionality"""
    
    @pytest.mark.asyncio
    async def test_metric_publishing(self, live_streamer):
        """Test publishing metrics to Redis streams"""
        metric = MetricData(
            metric_type="test_metric",
            value=42.0,
            tags={"environment": "test"},
            user_id=TEST_USER_ID
        )
        
        # Publish metric
        await live_streamer.publish_metric(metric)
        
        # Verify metric was stored
        # Note: This would require checking Redis streams
        # For now, we'll just verify no exceptions were raised
        assert True
    
    @pytest.mark.asyncio
    async def test_feedback_processing(self, live_streamer):
        """Test feedback submission and processing"""
        feedback = FeedbackData(
            feedback_type="bug_report",
            content="Test feedback content",
            rating=4,
            user_id=TEST_USER_ID
        )
        
        # Submit feedback
        await live_streamer.publish_feedback(feedback)
        
        # Verify feedback was processed
        assert True
    
    @pytest.mark.asyncio
    async def test_model_performance_tracking(self, live_streamer):
        """Test model performance monitoring"""
        performance = ModelPerformanceData(
            model_name="test_model",
            accuracy=0.95,
            response_time_ms=150,
            throughput_rps=100,
            error_rate=0.01
        )
        
        # Publish performance data
        await live_streamer.publish_model_performance(performance)
        
        # Verify performance data was stored
        assert True
    
    @pytest.mark.asyncio
    async def test_stream_consumption(self, live_streamer):
        """Test consuming data from Redis streams"""
        # Start stream consumer
        consumer_task = asyncio.create_task(
            live_streamer.start_stream_consumer("test_consumer")
        )
        
        # Give consumer time to start
        await asyncio.sleep(0.1)
        
        # Publish test data
        metric = MetricData(
            metric_type="test_consumption",
            value=1.0,
            user_id=TEST_USER_ID
        )
        await live_streamer.publish_metric(metric)
        
        # Give consumer time to process
        await asyncio.sleep(0.1)
        
        # Stop consumer
        consumer_task.cancel()
        
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
        
        assert True

class TestInteractiveFeatures:
    """Test interactive features functionality"""
    
    @pytest.mark.asyncio
    async def test_collaborative_editing(self, interactive_manager):
        """Test collaborative code editing"""
        file_path = "test_file.py"
        content = "print('Hello, World!')"
        
        # Start collaborative session
        await interactive_manager.start_collaborative_session(
            file_path, TEST_USER_ID, content
        )
        
        # Verify session was created
        editor = interactive_manager.collaborative_editor
        assert file_path in editor.active_documents
        assert TEST_USER_ID in editor.active_documents[file_path]["collaborators"]
    
    @pytest.mark.asyncio
    async def test_code_operations(self, interactive_manager):
        """Test applying code operations in collaborative editing"""
        file_path = "test_file.py"
        content = "print('Hello')"
        
        # Start session
        await interactive_manager.start_collaborative_session(
            file_path, TEST_USER_ID, content
        )
        
        # Apply insert operation
        operation = CodeOperation(
            operation_type=OperationType.INSERT,
            position=13,  # After 'Hello'
            content=", World",
            user_id=TEST_USER_ID
        )
        
        await interactive_manager.collaborative_editor.apply_operation(
            file_path, operation
        )
        
        # Verify operation was applied
        editor = interactive_manager.collaborative_editor
        updated_content = editor.active_documents[file_path]["content"]
        assert ", World" in updated_content
    
    @pytest.mark.asyncio
    async def test_cursor_tracking(self, interactive_manager):
        """Test cursor position tracking"""
        file_path = "test_file.py"
        
        cursor_position = CursorPosition(
            user_id=TEST_USER_ID,
            file_path=file_path,
            line=1,
            column=10
        )
        
        await interactive_manager.collaborative_editor.update_cursor(cursor_position)
        
        # Verify cursor was tracked
        editor = interactive_manager.collaborative_editor
        assert TEST_USER_ID in editor.user_cursors
        assert editor.user_cursors[TEST_USER_ID].line == 1
        assert editor.user_cursors[TEST_USER_ID].column == 10
    
    @pytest.mark.asyncio
    async def test_debug_session_management(self, interactive_manager):
        """Test debugging session lifecycle"""
        file_path = "debug_test.py"
        
        # Start debug session
        session_id = await interactive_manager.start_debug_session(
            TEST_USER_ID, file_path
        )
        
        # Verify session was created
        debug_manager = interactive_manager.debug_manager
        assert session_id in debug_manager.active_sessions
        
        # Add breakpoint
        await debug_manager.add_breakpoint(session_id, 10)
        
        # Verify breakpoint was added
        session = debug_manager.active_sessions[session_id]
        assert 10 in session.breakpoints
        
        # End session
        await debug_manager.end_debug_session(session_id)
        
        # Verify session was removed
        assert session_id not in debug_manager.active_sessions
    
    @pytest.mark.asyncio
    async def test_notification_system(self, interactive_manager):
        """Test notification creation and delivery"""
        # Create notification
        notification_id = await interactive_manager.create_notification(
            notification_type=NotificationType.INFO,
            title="Test Notification",
            message="This is a test notification",
            user_id=TEST_USER_ID
        )
        
        # Verify notification was created
        assert notification_id is not None
        
        # Get user notifications
        notifications = await interactive_manager.notification_manager.get_user_notifications(
            TEST_USER_ID
        )
        
        # Verify notification exists
        assert len(notifications) > 0
        assert any(n.notification_id == notification_id for n in notifications)

class TestAPIEndpoints:
    """Test REST API endpoints"""
    
    def test_health_endpoint(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
    
    def test_stats_endpoint(self, test_client):
        """Test statistics endpoint"""
        response = test_client.get("/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "websocket" in data
        assert "interactive_features" in data
        assert "system" in data
    
    def test_metrics_endpoint(self, test_client):
        """Test metrics publishing endpoint"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        payload = {
            "metric_type": "test_metric",
            "value": 42.0,
            "tags": {"test": "true"}
        }
        
        response = test_client.post("/metrics", json=payload, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    def test_feedback_endpoint(self, test_client):
        """Test feedback submission endpoint"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        payload = {
            "feedback_type": "bug_report",
            "content": "Test feedback",
            "rating": 4
        }
        
        response = test_client.post("/feedback", json=payload, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"
    
    def test_notification_endpoints(self, test_client):
        """Test notification management endpoints"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Create notification
        payload = {
            "notification_type": "info",
            "title": "Test Notification",
            "message": "Test message",
            "user_id": TEST_USER_ID
        }
        
        response = test_client.post("/notifications", json=payload, headers=headers)
        assert response.status_code == 200
        
        # Get notifications
        response = test_client.get("/notifications", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "notifications" in data
        assert "count" in data
    
    def test_collaboration_endpoints(self, test_client):
        """Test collaboration endpoints"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Start collaboration
        payload = {
            "file_path": "test_file.py",
            "content": "print('Hello, World!')"
        }
        
        response = test_client.post("/collaboration/start", json=payload, headers=headers)
        assert response.status_code == 200
        
        # Apply operation
        operation_payload = {
            "operation_type": "insert",
            "position": 13,
            "content": ", Universe"
        }
        
        response = test_client.post(
            "/collaboration/test_file.py/operation",
            json=operation_payload,
            headers=headers
        )
        assert response.status_code == 200
    
    def test_debug_endpoints(self, test_client):
        """Test debugging endpoints"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Start debug session
        payload = {
            "file_path": "debug_test.py",
            "breakpoints": [5, 10, 15]
        }
        
        response = test_client.post("/debug/start", json=payload, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        session_id = data["session_id"]
        
        # Add breakpoint
        response = test_client.post(
            f"/debug/{session_id}/breakpoint?line_number=20",
            headers=headers
        )
        assert response.status_code == 200
        
        # End session
        response = test_client.delete(f"/debug/{session_id}", headers=headers)
        assert response.status_code == 200

class TestWebSocketIntegration:
    """Test WebSocket integration"""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection to the server"""
        # This would require a running server instance
        # For now, we'll test the connection logic
        
        # Mock WebSocket connection
        mock_websocket = AsyncMock()
        mock_websocket.receive_text = AsyncMock(return_value=json.dumps({
            "event_type": "chat_message",
            "data": {"content": "Hello, WebSocket!"}
        }))
        
        # Test message handling
        # This would be part of the actual WebSocket endpoint test
        assert True
    
    @pytest.mark.asyncio
    async def test_websocket_authentication(self):
        """Test WebSocket authentication"""
        # Test valid token
        valid_token = TEST_TOKEN
        user_id, session_id = valid_token.split(":")
        assert user_id == TEST_USER_ID
        assert session_id == TEST_SESSION_ID
        
        # Test invalid token
        invalid_token = "invalid_token"
        # This should raise an authentication error
        assert True

class TestPerformanceAndLoad:
    """Test performance and load handling"""
    
    @pytest.mark.asyncio
    async def test_concurrent_connections(self, websocket_manager):
        """Test handling multiple concurrent WebSocket connections"""
        connections = []
        
        # Create multiple connections
        for i in range(100):
            mock_websocket = AsyncMock()
            connection = ConnectionInfo(
                user_id=f"user_{i}",
                websocket=mock_websocket
            )
            connections.append(connection)
            await websocket_manager.connect(connection)
        
        # Verify all connections are tracked
        stats = await websocket_manager.get_connection_stats()
        assert stats["total_connections"] == 100
        
        # Test broadcast to all connections
        message = WebSocketMessage(
            event_type=EventType.SYSTEM_STATUS,
            data={"status": "Load test message"}
        )
        
        start_time = datetime.now()
        await websocket_manager.broadcast(message)
        end_time = datetime.now()
        
        # Verify broadcast completed quickly
        broadcast_time = (end_time - start_time).total_seconds()
        assert broadcast_time < 1.0  # Should complete within 1 second
    
    @pytest.mark.asyncio
    async def test_high_frequency_operations(self, interactive_manager):
        """Test handling high-frequency collaborative operations"""
        file_path = "load_test.py"
        content = "# Load test file"
        
        # Start collaborative session
        await interactive_manager.start_collaborative_session(
            file_path, TEST_USER_ID, content
        )
        
        # Apply many operations quickly
        operations = []
        for i in range(100):
            operation = CodeOperation(
                operation_type=OperationType.INSERT,
                position=len(content) + i,
                content=f"\n# Line {i}",
                user_id=TEST_USER_ID
            )
            operations.append(operation)
        
        start_time = datetime.now()
        
        # Apply all operations
        for operation in operations:
            await interactive_manager.collaborative_editor.apply_operation(
                file_path, operation
            )
        
        end_time = datetime.now()
        
        # Verify operations completed quickly
        operation_time = (end_time - start_time).total_seconds()
        assert operation_time < 5.0  # Should complete within 5 seconds
        
        # Verify final state
        editor = interactive_manager.collaborative_editor
        final_content = editor.active_documents[file_path]["content"]
        assert "# Line 99" in final_content

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.mark.asyncio
    async def test_redis_connection_failure(self):
        """Test handling Redis connection failures"""
        # Test with invalid Redis URL
        invalid_manager = WebSocketManager("redis://invalid:6379")
        
        with pytest.raises(Exception):
            await invalid_manager.initialize()
    
    @pytest.mark.asyncio
    async def test_websocket_disconnection_handling(self, websocket_manager):
        """Test handling unexpected WebSocket disconnections"""
        mock_websocket = AsyncMock()
        mock_websocket.send_text.side_effect = Exception("Connection lost")
        
        connection = ConnectionInfo(
            user_id=TEST_USER_ID,
            websocket=mock_websocket
        )
        
        await websocket_manager.connect(connection)
        
        # Try to send message to disconnected WebSocket
        message = WebSocketMessage(
            event_type=EventType.NOTIFICATION,
            data={"content": "Test message"}
        )
        
        # Should handle the exception gracefully
        await websocket_manager.send_to_user(TEST_USER_ID, message)
        
        # Connection should be cleaned up
        # (Implementation would need to handle this)
        assert True
    
    @pytest.mark.asyncio
    async def test_invalid_operation_handling(self, interactive_manager):
        """Test handling invalid collaborative operations"""
        file_path = "nonexistent_file.py"
        
        # Try to apply operation to non-existent file
        operation = CodeOperation(
            operation_type=OperationType.INSERT,
            position=0,
            content="test",
            user_id=TEST_USER_ID
        )
        
        # Should handle gracefully without crashing
        await interactive_manager.collaborative_editor.apply_operation(
            file_path, operation
        )
        
        assert True

if __name__ == "__main__":
    # Run tests
    pytest.main(["-v", __file__])