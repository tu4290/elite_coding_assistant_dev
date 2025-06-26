# Persistent Knowledge Graph MCP Documentation

## Overview
The Persistent Knowledge Graph MCP serves as the central intelligence hub and absolute authority for all project decisions. It manages long-term project knowledge, entity relationships, system intelligence, and project history.

## Server Configuration
```json
"knowledge-graph": {
  "command": "uvx",
  "args": ["mcp-knowledge-graph"]
}
```

## Available Tools

### 1. create_entities
**Description:** Create multiple new entities in the knowledge graph
**Parameters:**
- `entities`: Array of entity objects with name, entityType, and observations
**Usage:** Adding new project components, features, or concepts

### 2. create_relations
**Description:** Create multiple new relations between entities in the knowledge graph. Relations should be in active voice
**Parameters:**
- `relations`: Array of relation objects with from, to, and relationType
**Usage:** Establishing connections between project elements

### 3. add_observations
**Description:** Add new observations to existing entities in the knowledge graph
**Parameters:**
- `observations`: Array with entityName and contents array
**Usage:** Updating entity knowledge with new insights

### 4. delete_entities
**Description:** Delete multiple entities and their associated relations from the knowledge graph
**Parameters:**
- `entityNames`: Array of entity names to delete
**Usage:** Removing obsolete project elements

### 5. delete_observations
**Description:** Delete specific observations from entities in the knowledge graph
**Parameters:**
- `deletions`: Array with entityName and observations to delete
**Usage:** Cleaning up outdated or incorrect information

### 6. delete_relations
**Description:** Delete multiple relations from the knowledge graph
**Parameters:**
- `relations`: Array of relations to delete with from, to, and relationType
**Usage:** Removing obsolete connections

### 7. read_graph
**Description:** Read the entire knowledge graph
**Usage:** Complete project intelligence overview

### 8. search_nodes
**Description:** Search for nodes in the knowledge graph based on a query
**Parameters:**
- `query`: Search query to match against entity names, types, and observation content
**Usage:** Finding specific project information

### 9. open_nodes
**Description:** Open specific nodes in the knowledge graph by their names
**Parameters:**
- `names`: Array of entity names to retrieve
**Usage:** Detailed examination of specific entities

### 10. update_entities
**Description:** Update multiple existing entities in the knowledge graph
**Parameters:**
- `entities`: Array with name, entityType, and observations updates
**Usage:** Modifying existing project elements

### 11. update_relations
**Description:** Update multiple existing relations in the knowledge graph
**Parameters:**
- `relations`: Array with from, to, and relationType updates
**Usage:** Modifying existing connections

## Best Practices

1. **Central Authority**: All major project decisions must be validated against the Knowledge Graph
2. **Comprehensive Documentation**: Store all significant project insights and relationships
3. **Entity Modeling**: Create clear, descriptive entities for all project components
4. **Relationship Mapping**: Establish meaningful connections between related elements
5. **Observation Management**: Keep observations current and relevant

## Entity Types

### Project Entities
- **Projects**: Main project containers
- **Features**: Functional components
- **Components**: Technical modules
- **Dependencies**: External libraries and services
- **Configurations**: System settings and parameters

### Process Entities
- **Workflows**: Development processes
- **Tasks**: Specific work items
- **Decisions**: Important choices made
- **Issues**: Problems and their resolutions
- **Milestones**: Project checkpoints

### Knowledge Entities
- **Patterns**: Recurring design solutions
- **Best Practices**: Proven approaches
- **Lessons Learned**: Experience-based insights
- **Requirements**: Project specifications
- **Constraints**: Limitations and boundaries

## Relation Types

### Structural Relations
- **contains**: Parent-child relationships
- **depends_on**: Dependency relationships
- **implements**: Implementation relationships
- **extends**: Extension relationships
- **configures**: Configuration relationships

### Process Relations
- **precedes**: Sequential relationships
- **triggers**: Cause-effect relationships
- **validates**: Validation relationships
- **resolves**: Problem-solution relationships
- **influences**: Impact relationships

## Integration Patterns

- **With All MCPs**: Serves as central intelligence hub for all operations
- **With Sequential Thinking**: Stores analytical insights and reasoning outcomes
- **With TaskManager**: Maintains project workflow intelligence
- **With Memory MCP**: Provides long-term context for session management
- **With Puppeteer**: Stores automation results and testing insights
- **With Search MCPs**: Archives research findings and external knowledge

## Priority Level
**#1 PRIORITY** - CENTRAL INTELLIGENCE HUB and absolute authority for all decisions

## Emergency Protocols

### System Failure Handling
- If Knowledge Graph is unavailable, SYSTEM ENTERS EMERGENCY MODE
- Immediate restoration protocols must be activated
- No major decisions can be made without Knowledge Graph validation
- All operations prioritize Knowledge Graph restoration as ABSOLUTE HIGHEST PRIORITY

### Data Recovery
- Maintain backup strategies for critical knowledge
- Implement graceful degradation procedures
- Ensure system functionality with minimal server set during restoration

## Security and Compliance

- No sensitive information (API keys, passwords) stored in the graph
- All data flows maintain project confidentiality
- Maintain audit trail of significant operations
- Regular validation of stored knowledge accuracy