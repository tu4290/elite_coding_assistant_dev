# Puppeteer MCP Documentation

## Overview
The Puppeteer MCP enables web automation, UI testing, data scraping, real-time monitoring, screenshot capture, and form automation capabilities for comprehensive web interaction.

## Server Configuration
```json
"puppeteer": {
  "command": "uvx",
  "args": ["mcp-puppeteer"]
}
```

## Available Tools

*Note: The Puppeteer MCP tools are currently not accessible in the provided interface, but based on the MCP architecture, typical Puppeteer MCP tools include:*

### Expected Web Automation Operations

#### Browser Management
- **launch_browser**: Start a new browser instance
- **close_browser**: Terminate browser session
- **new_page**: Create a new browser tab/page
- **close_page**: Close specific browser tab/page
- **set_viewport**: Configure browser viewport size

#### Navigation and Interaction
- **navigate_to**: Navigate to a specific URL
- **click_element**: Click on page elements
- **type_text**: Input text into form fields
- **select_option**: Select dropdown options
- **submit_form**: Submit web forms
- **scroll_page**: Scroll page content

#### Data Extraction
- **extract_text**: Extract text content from elements
- **extract_attributes**: Get element attributes
- **extract_links**: Collect all page links
- **scrape_table**: Extract table data
- **get_page_source**: Retrieve full page HTML

#### Visual Operations
- **take_screenshot**: Capture page screenshots
- **take_element_screenshot**: Screenshot specific elements
- **generate_pdf**: Create PDF from page content
- **record_video**: Record browser interactions

#### Testing and Validation
- **wait_for_element**: Wait for elements to appear
- **wait_for_navigation**: Wait for page loads
- **assert_element_exists**: Validate element presence
- **assert_text_content**: Verify text content
- **check_page_performance**: Analyze page metrics

## Best Practices

1. **Web Automation**: Automate repetitive web tasks and data collection
2. **UI Testing**: Implement end-to-end testing of web applications
3. **Data Validation**: Real-time validation of web-based information
4. **Performance Monitoring**: Continuous monitoring of web application performance
5. **Screenshot Documentation**: Visual documentation and audit trails

## Use Cases

### Financial Data Collection (Elite Options System)
- Real-time options flow monitoring from web sources
- Automated data validation against multiple financial providers
- Capture screenshots of trading interfaces for audit trails
- Monitor competitor platforms for market intelligence

### Automated Testing
- End-to-end testing of dashboard functionality
- User interface testing for options analytics displays
- Validation of real-time data updates and alert systems
- Responsive design testing across multiple screen sizes

### Data Collection and Monitoring
- Web scraping for market data and news
- Real-time monitoring of external APIs and services
- Automated form submissions and data entry
- Continuous monitoring of application health

### Quality Assurance
- Visual regression testing
- Performance benchmarking
- Accessibility testing
- Cross-browser compatibility validation

## Integration Patterns

- **With Search MCPs**: Automate search result validation and data extraction
- **With Persistent Knowledge Graph**: Store automation results and testing insights
- **With TaskManager**: Automated testing tasks and validation workflows
- **With Sequential Thinking**: Systematic testing and validation workflows
- **With Memory MCP**: Track automation results and browser state
- **With Context7**: Advanced pattern recognition in web data

## Priority Level
**#6 Priority** in the MCP hierarchy - Web automation, testing, and data collection

## Automation Workflows

### Market Analysis Workflow
```
TaskManager (plan analysis) → 
Sequential Thinking (strategy) → 
Brave Search (market news) → 
Puppeteer (data collection & validation) → 
Persistent Knowledge Graph (store insights)
```

### Testing and QA Workflow
```
TaskManager (test planning) → 
Puppeteer (UI automation) → 
Memory (test results) → 
Sequential Thinking (analysis) → 
Persistent Knowledge Graph (quality metrics)
```

### Real-time Monitoring Workflow
```
Puppeteer (continuous monitoring) → 
Context7 (anomaly detection) → 
Brave Search (news correlation) → 
Persistent Knowledge Graph (alert history)
```

## Security and Compliance

### Financial Data Security
- Comply with financial data regulations
- Implement secure credential management for trading platforms
- Maintain audit trails of all automated data collection
- Ensure compliance with market data licensing agreements

### Performance Standards
- Operations must not impact real-time trading performance
- Implement circuit breakers for automated data collection
- Monitor and optimize resource usage during market hours
- Maintain sub-second response times for critical operations

## Configuration Options

### Browser Settings
- Headless vs. headed mode
- Custom user agents
- Proxy configuration
- Cookie and session management
- JavaScript execution control

### Performance Optimization
- Resource blocking (images, CSS, fonts)
- Network throttling simulation
- Cache management
- Concurrent operation limits
- Memory usage optimization

## Error Handling

### Common Issues
- Element not found errors
- Network timeout handling
- Page load failures
- JavaScript execution errors
- Browser crash recovery

### Recovery Strategies
- Automatic retry mechanisms
- Fallback navigation paths
- Error screenshot capture
- Graceful degradation
- Alternative data sources

## Monitoring and Metrics

### Performance Metrics
- Page load times
- Element interaction latency
- Memory usage tracking
- CPU utilization monitoring
- Network request analysis

### Success Metrics
- Automation success rates
- Data extraction accuracy
- Test pass/fail ratios
- Error frequency tracking
- Performance benchmarks