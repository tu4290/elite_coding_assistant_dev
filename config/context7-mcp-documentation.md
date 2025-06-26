# Context7 MCP Documentation

## Overview
The Context7 MCP provides specialized context management, advanced analysis, contextual intelligence, and pattern recognition capabilities for enhanced project understanding and decision-making.

## Server Configuration
```json
"context7": {
  "command": "uvx",
  "args": ["mcp-context7"]
}
```

## Available Tools

### 1. resolve-library-id
**Description:** Resolves a package/product name to a Context7-compatible library identifier
**Parameters:**
- `libraryName` (string, required): The name of the library to resolve (e.g., "requests", "numpy", "react")
**Usage:** Library identification and compatibility checking
**Example:** Search for "requests" returns multiple matches with trust scores and snippet counts

### 2. get-library-docs
**Description:** Fetches up-to-date documentation for a library. You must call 'resolve-library-id' first to get the proper library identifier
**Parameters:**
- `context7CompatibleLibraryID` (string, required): The library ID from resolve-library-id (e.g., "/psf/requests")
**Usage:** Retrieving current library documentation and API references
**Example:** Using ID "/psf/requests" returns comprehensive documentation with 140+ code snippets

## Best Practices

1. **Library Resolution**: Always use resolve-library-id before fetching documentation
2. **Documentation Access**: Leverage get-library-docs for up-to-date API information
3. **Context Analysis**: Use for specialized context management and analysis
4. **Pattern Recognition**: Apply for identifying recurring patterns in code and data
5. **Advanced Intelligence**: Utilize for complex contextual decision-making
6. **Parameter Accuracy**: Use exact parameter names: `libraryName` for resolution, `context7CompatibleLibraryID` for docs
7. **Trust Score Evaluation**: Consider trust scores when selecting from multiple library matches
8. **Comprehensive Documentation**: Leverage the extensive code snippets and examples provided

## Practical Usage Examples

### Successful Context7 Workflow
```
1. Call resolve-library-id with libraryName: "requests"
   - Returns: ["/psf/requests" (Trust: 7.3, 140 snippets), "/wangluozhe/requests" (Trust: 8.3, 33 snippets), etc.]
   - Select highest trust score or most snippets based on needs

2. Call get-library-docs with context7CompatibleLibraryID: "/psf/requests"
   - Returns: Comprehensive documentation with 140+ code snippets
   - Covers: HTTP methods, authentication, JSON handling, file uploads, sessions, timeouts, error handling
```

### Common Parameter Errors to Avoid
- ❌ Using `query` instead of `libraryName` for resolve-library-id
- ❌ Using `libraryId` instead of `context7CompatibleLibraryID` for get-library-docs
- ✅ Always use exact parameter names as specified in the tool schema

## Use Cases

### Library and Documentation Management
- Resolve library identifiers for compatibility checking
- Fetch current documentation for development libraries
- Validate API usage against latest documentation
- Ensure compatibility with project dependencies

### Context Analysis
- Advanced contextual intelligence for project decisions
- Pattern recognition in code and system architecture
- Contextual analysis of user requirements and specifications
- Intelligent context switching and management

### Development Support
- Real-time access to library documentation
- API reference validation and verification
- Dependency analysis and compatibility checking
- Code pattern analysis and optimization suggestions

## Integration Patterns

- **With Persistent Knowledge Graph**: Advanced context analysis enhances long-term project intelligence
- **With Sequential Thinking**: Provides contextual depth to analytical reasoning
- **With Memory MCP**: Enhances session context with advanced analytical capabilities
- **With Puppeteer**: Advanced pattern recognition in web data and automation results
- **With Search MCPs**: Contextual analysis of search results and research findings
- **With TaskManager**: Contextual intelligence for task planning and execution

## Priority Level
**#7 Priority** in the MCP hierarchy - Specialized context analysis and advanced intelligence

## Workflow Examples

### Library Documentation Workflow
```
1. resolve-library-id (get proper identifier)
2. get-library-docs (fetch current documentation)
3. Store results in Persistent Knowledge Graph
4. Update Memory MCP with session context
```

### Advanced Context Analysis Workflow
```
Context7 (pattern analysis) → 
Sequential Thinking (structured reasoning) → 
Persistent Knowledge Graph (store insights) → 
Memory (session tracking)
```

### Development Support Workflow
```
Context7 (library resolution) → 
Context7 (documentation fetch) → 
Sequential Thinking (analysis) → 
TaskManager (implementation planning)
```

## Advanced Features

### Contextual Intelligence
- **Pattern Recognition**: Identify recurring patterns in code, data, and workflows
- **Context Switching**: Intelligent management of multiple project contexts
- **Relationship Analysis**: Understanding complex relationships between project elements
- **Predictive Analysis**: Anticipate potential issues and optimization opportunities

### Library Management
- **Identifier Resolution**: Convert library names to standardized identifiers
- **Documentation Retrieval**: Access to current and comprehensive library documentation
- **Version Compatibility**: Analysis of library version compatibility
- **API Validation**: Verification of API usage against current specifications

### Decision Support
- **Contextual Recommendations**: Intelligent suggestions based on project context
- **Risk Assessment**: Analysis of potential risks and mitigation strategies
- **Optimization Opportunities**: Identification of performance and efficiency improvements
- **Best Practice Guidance**: Context-aware best practice recommendations

## Data Processing

### Input Processing
- **Multi-format Support**: Handle various data formats and structures
- **Context Extraction**: Extract relevant context from complex data sources
- **Pattern Detection**: Identify meaningful patterns in input data
- **Relationship Mapping**: Map relationships between data elements

### Output Generation
- **Structured Analysis**: Provide well-organized analytical outputs
- **Actionable Insights**: Generate concrete recommendations and next steps
- **Context Summaries**: Create comprehensive context summaries
- **Pattern Reports**: Detailed reports on identified patterns and trends

## Performance Characteristics

### Analysis Speed
- **Real-time Processing**: Fast analysis of context and patterns
- **Efficient Algorithms**: Optimized for quick pattern recognition
- **Scalable Architecture**: Handle varying complexity levels
- **Responsive Interface**: Minimal latency for user interactions

### Accuracy and Reliability
- **High Precision**: Accurate pattern recognition and context analysis
- **Consistent Results**: Reliable and repeatable analytical outputs
- **Error Detection**: Built-in validation and error checking
- **Quality Assurance**: Continuous monitoring of analysis quality

## Security and Privacy

### Data Protection
- **Context Isolation**: Secure separation of different project contexts
- **Privacy Preservation**: Protection of sensitive project information
- **Access Control**: Controlled access to contextual intelligence
- **Audit Trails**: Comprehensive logging of context analysis activities

### Compliance
- **Data Governance**: Adherence to data governance policies
- **Regulatory Compliance**: Compliance with relevant regulations
- **Security Standards**: Implementation of industry security standards
- **Privacy Regulations**: Compliance with privacy protection requirements

## Troubleshooting

### Common Issues
- **Library Resolution Failures**: Handle cases where library identifiers cannot be resolved
- **Documentation Access Errors**: Manage failures in documentation retrieval
- **Context Analysis Limitations**: Address limitations in complex context analysis
- **Performance Bottlenecks**: Identify and resolve performance issues

### Resolution Strategies
- **Fallback Mechanisms**: Alternative approaches when primary methods fail
- **Error Recovery**: Automatic recovery from common error conditions
- **Performance Optimization**: Strategies for improving analysis performance
- **User Guidance**: Clear guidance for resolving user-facing issues