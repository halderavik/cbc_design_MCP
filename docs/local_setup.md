# Local Setup Guide for CBC Design Generator MCP Server

This guide provides comprehensive instructions for setting up and running the CBC Design Generator MCP Server locally for development, testing, and demonstration purposes.

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended for large designs)
- **Storage**: 1GB free space for dependencies and generated files

### Required Software
- Python 3.11+ with pip
- Git (for version control)
- A text editor or IDE (VS Code, PyCharm, etc.)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd CBC_design_MCP
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install production dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### 4. Verify Installation
```bash
# Run tests to verify installation
pytest -q

# Test the server directly
python -m conjoint_mcp.server
```

## Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
# Application settings
APP_VERSION=0.1.0
LOG_LEVEL=INFO

# Performance settings
MAX_RESPONSE_TIME=30
MAX_MEMORY_USAGE=500MB

# Development settings
DEBUG=false
```

### Settings File
The application uses Pydantic settings for configuration. Key settings include:

- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `max_response_time`: Maximum allowed response time in seconds
- `max_memory_usage`: Maximum memory usage threshold

## Running the Server

### Basic Server Startup
```bash
# Start the MCP server
python -m conjoint_mcp.server

# Or use the installed script
conjoint-mcp
```

### Server Modes
The server supports different modes:

1. **Stdio Mode** (default): Communicates via standard input/output
2. **HTTP Mode**: Communicates via HTTP (if implemented)

### Testing the Server
```bash
# Test with a simple request
echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m conjoint_mcp.server
```

## Local Testing Tools

### 1. Local Test Suite
The comprehensive test suite provides automated testing capabilities:

```bash
# Run all tests
python scripts/local_test_suite.py

# Run specific tests
python scripts/local_test_suite.py --test health
python scripts/local_test_suite.py --test generate
python scripts/local_test_suite.py --test benchmark
```

### 2. Interactive Tester
Interactive command-line interface for manual testing:

```bash
python scripts/interactive_tester.py
```

Features:
- Load sample scenarios
- Create custom scenarios
- Generate designs with different algorithms
- Optimize parameters
- Export designs
- View session history

### 3. Performance Monitor
Real-time performance monitoring and benchmarking:

```bash
# Run load test
python scripts/performance_monitor.py --load-test 100

# Continuous monitoring
python scripts/performance_monitor.py --monitor 300

# Generate performance report
python scripts/performance_monitor.py --report

# Generate performance plots
python scripts/performance_monitor.py --plot performance.png
```

### 4. Sample Scenarios
Pre-defined scenarios for testing and demonstration:

```bash
# List available scenarios
python scripts/sample_scenarios.py --list

# Get specific scenario
python scripts/sample_scenarios.py --scenario clothing

# Save scenario to file
python scripts/sample_scenarios.py --scenario electronics --save electronics.json
```

## Development Workflow

### 1. Code Quality Tools
```bash
# Format code
black src/ tests/ scripts/

# Lint code
flake8 src/ tests/ scripts/

# Type checking
mypy src/

# Run all quality checks
pre-commit run --all-files
```

### 2. Testing Workflow
```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run all tests with coverage
pytest --cov=src/conjoint_mcp

# Run specific test file
pytest tests/unit/test_health.py -v
```

### 3. Development Server
For development, you can run the server with additional logging:

```bash
# Set debug mode
export LOG_LEVEL=DEBUG
python -m conjoint_mcp.server
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError` when running scripts
**Solution**: Ensure virtual environment is activated and dependencies are installed
```bash
pip install -e .
```

#### 2. Permission Errors
**Problem**: Permission denied when running scripts
**Solution**: Make scripts executable or run with Python
```bash
python scripts/local_test_suite.py
```

#### 3. Port Conflicts
**Problem**: Server fails to start due to port conflicts
**Solution**: Check for running processes and kill them
```bash
# Find processes using the port
netstat -ano | findstr :8080
# Kill process (Windows)
taskkill /PID <process_id> /F
```

#### 4. Memory Issues
**Problem**: Out of memory errors with large designs
**Solution**: Reduce design size or increase system memory
```bash
# Monitor memory usage
python scripts/performance_monitor.py --monitor 60
```

### Debug Mode
Enable debug mode for detailed logging:

```bash
export LOG_LEVEL=DEBUG
python -m conjoint_mcp.server
```

### Log Files
Logs are written to stdout by default. To save logs to file:

```bash
python -m conjoint_mcp.server > server.log 2>&1
```

## Performance Optimization

### 1. System Optimization
- Use SSD storage for better I/O performance
- Ensure adequate RAM (8GB+ recommended)
- Close unnecessary applications

### 2. Python Optimization
```bash
# Use optimized Python build
python -O -m conjoint_mcp.server

# Set environment variables for optimization
export PYTHONOPTIMIZE=1
export PYTHONUNBUFFERED=1
```

### 3. Algorithm Selection
- Use `random` for fastest generation
- Use `doptimal` for best statistical properties
- Use `balanced` for moderate performance and quality

## Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique values for production
- Rotate secrets regularly

### 2. Input Validation
- All inputs are validated using Pydantic
- Malformed requests are rejected with appropriate error codes
- No sensitive data is logged

### 3. Resource Limits
- Response time limits prevent DoS attacks
- Memory usage monitoring prevents resource exhaustion
- Request rate limiting (if implemented)

## Backup and Recovery

### 1. Configuration Backup
```bash
# Backup configuration files
cp .env .env.backup
cp pyproject.toml pyproject.toml.backup
```

### 2. Data Backup
```bash
# Backup generated designs
tar -czf designs_backup.tar.gz exports/
```

### 3. Recovery
```bash
# Restore configuration
cp .env.backup .env

# Restore data
tar -xzf designs_backup.tar.gz
```

## Monitoring and Maintenance

### 1. Health Checks
```bash
# Regular health checks
python scripts/local_test_suite.py --test health
```

### 2. Performance Monitoring
```bash
# Daily performance reports
python scripts/performance_monitor.py --report > daily_report.txt
```

### 3. Log Analysis
```bash
# Analyze server logs
grep "ERROR" server.log
grep "WARNING" server.log
```

## Support and Resources

### 1. Documentation
- API documentation: `docs/api.md`
- Algorithm documentation: `docs/algorithms.md`
- Troubleshooting guide: `docs/troubleshooting.md`

### 2. Community
- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share ideas

### 3. Professional Support
- Contact information for enterprise support
- Training and consulting services

## Next Steps

After completing local setup:

1. **Explore the interactive tester** to understand the system
2. **Run the performance monitor** to establish baselines
3. **Try different sample scenarios** to see capabilities
4. **Create custom scenarios** for your specific use case
5. **Review the API documentation** for integration details

For production deployment, see the deployment guide in `docs/deployment.md`.
