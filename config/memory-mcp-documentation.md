# Memory MCP Documentation

## Overview
The Memory MCP manages session-specific knowledge and context, providing dynamic information storage and conversation continuity across all tool interactions.

## Server Configuration
```json
"memory": {
  "command": "uvx",
  "args": ["mcp-memory"]
}
```

## Available Tools

*Note: The Memory MCP tools are currently not accessible in the provided interface, but based on the MCP architecture, typical Memory MCP tools include:*

### Expected Memory Operations

#### Session Management
- **store_memory**: Store information in session memory
- **retrieve_memory**: Retrieve stored session information
- **update_memory**: Update existing memory entries
- **delete_memory**: Remove obsolete memory entries
- **search_memory**: Search through session memory

#### Context Management
- **set_context**: Establish session context
- **get_context**: Retrieve current session context
- **update_context**: Modify session context
- **clear_context**: Reset session context

#### Conversation Continuity
- **store_conversation**: Save conversation state
- **retrieve_conversation**: Load conversation history
- **summarize_session**: Create session summaries
- **track_interactions**: Monitor tool interactions

## Best Practices

1. **Session Context**: Maintain continuity across all tool interactions
2. **Dynamic Information**: Store temporary but important session data
3. **Conversation Tracking**: Keep track of user preferences and decisions
4. **Performance Optimization**: Cache frequently accessed information
5. **Resource Management**: Clean up obsolete session data regularly

## Use Cases

### Session Management
- User preferences and settings
- Current work context and focus
- Recent decisions and choices
- Active project state
- Temporary calculations and results

### Conversation Continuity
- Multi-turn conversation context
- Reference to previous discussions
- User feedback and corrections
- Iterative development progress
- Session-specific customizations

### Performance Optimization
- Caching of frequently accessed data
- Temporary storage of computation results
- Quick access to recent operations
- Reduced redundant API calls
- Optimized workflow patterns

## Integration Patterns

- **With Persistent Knowledge Graph**: Provides session context for long-term intelligence
- **With TaskManager**: Maintains task workflow continuity
- **With Sequential Thinking**: Preserves analytical context across reasoning sessions
- **With Puppeteer**: Tracks automation results and browser state
- **With Search MCPs**: Caches search results and research context
- **With Context7**: Enhances contextual analysis with session data

## Priority Level
**#3 Priority** in the MCP hierarchy - Session context and dynamic knowledge management

## Data Types

### Session Data
- Current user preferences
- Active project context
- Recent tool interactions
- Temporary variables and state
- Session-specific configurations

### Conversation Data
- User input history
- Assistant response patterns
- Feedback and corrections
- Iterative refinements
- Context switches and topics

### Performance Data
- Cached computation results
- Frequently accessed information
- Recent search results
- Tool usage patterns
- Optimization metrics

## Memory Management

### Storage Strategy
- **Short-term**: Current session data
- **Medium-term**: Recent conversation history
- **Temporary**: Computation caches and results
- **Volatile**: Real-time state and variables

### Cleanup Policies
- Regular cleanup of obsolete session data
- Automatic expiration of temporary caches
- Size-based memory management
- Priority-based retention policies

## Error Handling

### Memory Failures
- Graceful degradation when memory is unavailable
- Fallback to stateless operation mode
- Recovery procedures for corrupted session data
- Backup and restore capabilities

### Data Consistency
- Validation of stored session data
- Conflict resolution for concurrent updates
- Synchronization with other MCP servers
- Integrity checks and verification

## Security Considerations

- No persistent storage of sensitive information
- Session-scoped data isolation
- Automatic cleanup on session termination
- Secure handling of temporary credentials
- Privacy protection for user data

## Performance Characteristics

- **Fast Access**: Optimized for quick retrieval
- **Low Latency**: Minimal overhead for operations
- **Scalable**: Handles varying session sizes
- **Efficient**: Minimal resource consumption
- **Responsive**: Real-time updates and access