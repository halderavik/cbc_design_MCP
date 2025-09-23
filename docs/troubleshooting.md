# CBC Design Generator MCP Server - Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the CBC Design Generator MCP Server.

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Server Issues](#server-issues)
4. [Request/Response Issues](#requestresponse-issues)
5. [Performance Issues](#performance-issues)
6. [Integration Issues](#integration-issues)
7. [Error Codes Reference](#error-codes-reference)
8. [Debugging Tools](#debugging-tools)

## Quick Diagnostics

### Health Check
First, verify the server is working:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m conjoint_mcp.server
```

**Expected Output:**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"status": "ok", "version": "0.1.0"}}
```

### Basic Test
Test design generation:
```bash
echo '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "design.generate",
  "params": {
    "method": "random",
    "grid": {
      "attributes": [
        {
          "name": "Color",
          "levels": [{"name": "Red"}, {"name": "Blue"}]
        }
      ]
    },
    "options_per_screen": 2,
    "num_screens": 3
  }
}' | python -m conjoint_mcp.server
```

## Installation Issues

### Issue: Module Not Found
**Error:** `ModuleNotFoundError: No module named 'conjoint_mcp'`

**Solutions:**
1. **Install in development mode:**
   ```bash
   pip install -e .
   ```

2. **Check Python path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

3. **Verify installation:**
   ```bash
   pip list | grep conjoint
   ```

### Issue: Missing Dependencies
**Error:** `ImportError: No module named 'pydantic'`

**Solutions:**
1. **Install dependencies:**
   ```bash
   pip install -e .
   ```

2. **Install specific missing package:**
   ```bash
   pip install pydantic pydantic-settings numpy scipy
   ```

3. **Check requirements:**
   ```bash
   pip check
   ```

### Issue: Virtual Environment Problems
**Error:** Package installed but not found

**Solutions:**
1. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Verify activation:**
   ```bash
   which python
   pip list
   ```

3. **Recreate virtual environment:**
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -e .
   ```

## Server Issues

### Issue: Server Won't Start
**Error:** `python -m conjoint_mcp.server` hangs or fails

**Solutions:**
1. **Check for syntax errors:**
   ```bash
   python -m py_compile src/conjoint_mcp/server.py
   ```

2. **Run with verbose output:**
   ```bash
   python -v -m conjoint_mcp.server
   ```

3. **Check for port conflicts:**
   ```bash
   # Windows
   netstat -ano | findstr :8080
   
   # macOS/Linux
   lsof -i :8080
   ```

4. **Test with minimal request:**
   ```bash
   echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | timeout 10 python -m conjoint_mcp.server
   ```

### Issue: Server Crashes
**Error:** Server exits unexpectedly

**Solutions:**
1. **Check error logs:**
   ```bash
   python -m conjoint_mcp.server 2>&1 | tee server.log
   ```

2. **Run with debug mode:**
   ```bash
   export LOG_LEVEL=DEBUG
   python -m conjoint_mcp.server
   ```

3. **Check system resources:**
   ```bash
   # Memory usage
   free -h  # Linux
   vm_stat  # macOS
   
   # Disk space
   df -h
   ```

4. **Test with smaller designs:**
   ```bash
   # Use minimal design
   echo '{
     "jsonrpc": "2.0",
     "id": 1,
     "method": "design.generate",
     "params": {
       "method": "random",
       "grid": {
         "attributes": [
           {
             "name": "A",
             "levels": [{"name": "1"}, {"name": "2"}]
           }
         ]
       },
       "options_per_screen": 2,
       "num_screens": 2
     }
   }' | python -m conjoint_mcp.server
   ```

### Issue: Permission Denied
**Error:** `PermissionError: [Errno 13] Permission denied`

**Solutions:**
1. **Check file permissions:**
   ```bash
   ls -la src/conjoint_mcp/server.py
   ```

2. **Run with appropriate permissions:**
   ```bash
   # Make executable
   chmod +x src/conjoint_mcp/server.py
   
   # Or run with Python
   python -m conjoint_mcp.server
   ```

3. **Check directory permissions:**
   ```bash
   ls -la .
   ```

## Request/Response Issues

### Issue: Invalid JSON
**Error:** `json.decoder.JSONDecodeError`

**Solutions:**
1. **Validate JSON format:**
   ```bash
   echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m json.tool
   ```

2. **Check for trailing commas:**
   ```json
   // Wrong
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "health",
     "params": {},
   }
   
   // Correct
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "health",
     "params": {}
   }
   ```

3. **Use proper escaping:**
   ```bash
   # Use single quotes for shell, double quotes for JSON
   echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}'
   ```

### Issue: Method Not Found
**Error:** `{"error": {"code": -32601, "message": "Method not found"}}`

**Solutions:**
1. **Check method name spelling:**
   ```json
   // Correct methods
   "method": "health"
   "method": "design.generate"
   "method": "design.optimize"
   "method": "design.export"
   ```

2. **Verify JSON-RPC format:**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "health",
     "params": {}
   }
   ```

3. **Test with health check first:**
   ```bash
   echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m conjoint_mcp.server
   ```

### Issue: Invalid Parameters
**Error:** `{"error": {"code": -32602, "message": "Invalid params"}}`

**Solutions:**
1. **Check parameter structure:**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "design.generate",
     "params": {
       "method": "random",
       "grid": {
         "attributes": [
           {
             "name": "Color",
             "levels": [{"name": "Red"}, {"name": "Blue"}]
           }
         ]
       },
       "options_per_screen": 3,
       "num_screens": 10
     }
   }
   ```

2. **Validate required fields:**
   - `method` (string): Algorithm name
   - `grid` (object): Design grid with attributes
   - `attributes` (array): List of attributes
   - `name` (string): Attribute name
   - `levels` (array): List of levels

3. **Check data types:**
   ```json
   {
     "options_per_screen": 3,    // integer, not string
     "num_screens": 10,          // integer, not string
     "target_power": 0.8         // number, not string
   }
   ```

### Issue: Empty Response
**Error:** No response or empty response

**Solutions:**
1. **Check request format:**
   ```bash
   # Ensure proper line ending
   echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m conjoint_mcp.server
   ```

2. **Add timeout:**
   ```bash
   timeout 30 echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m conjoint_mcp.server
   ```

3. **Check for hanging processes:**
   ```bash
   # Kill any hanging Python processes
   pkill -f conjoint_mcp
   
   # Or on Windows
   taskkill /f /im python.exe
   ```

4. **Test with interactive mode:**
   ```bash
   python scripts/interactive_tester.py
   ```

## Performance Issues

### Issue: Slow Response Times
**Error:** Requests take too long (>30 seconds)

**Solutions:**
1. **Reduce design complexity:**
   ```json
   {
     "options_per_screen": 3,    // Reduce from 5
     "num_screens": 10,          // Reduce from 20
     "attributes": [             // Reduce number of attributes
       {
         "name": "Color",
         "levels": [{"name": "Red"}, {"name": "Blue"}]  // Reduce levels
       }
     ]
   }
   ```

2. **Use faster algorithms:**
   ```json
   {
     "method": "random"  // Instead of "doptimal"
   }
   ```

3. **Monitor performance:**
   ```bash
   python scripts/performance_monitor.py --load-test 10
   ```

4. **Check system resources:**
   ```bash
   # CPU usage
   top
   
   # Memory usage
   free -h
   
   # Disk I/O
   iostat
   ```

### Issue: Memory Errors
**Error:** `MemoryError` or out of memory

**Solutions:**
1. **Reduce design size:**
   ```json
   {
     "num_screens": 5,           // Reduce from 20
     "options_per_screen": 3,    // Reduce from 5
     "attributes": [             // Reduce attributes
       {
         "name": "Color",
         "levels": [{"name": "Red"}, {"name": "Blue"}]  // Reduce levels
       }
     ]
   }
   ```

2. **Use simpler algorithms:**
   ```json
   {
     "method": "random"  // Instead of "doptimal"
   }
   ```

3. **Increase system memory:**
   ```bash
   # Check available memory
   free -h
   
   # Close other applications
   # Consider upgrading RAM
   ```

4. **Monitor memory usage:**
   ```bash
   python scripts/performance_monitor.py --monitor 60
   ```

### Issue: High CPU Usage
**Error:** Server uses too much CPU

**Solutions:**
1. **Use less intensive algorithms:**
   ```json
   {
     "method": "random"  // Instead of "doptimal"
   }
   ```

2. **Reduce design complexity:**
   ```json
   {
     "num_screens": 5,           // Reduce from 20
     "options_per_screen": 3,    // Reduce from 5
     "attributes": [             // Reduce attributes
       {
         "name": "Color",
         "levels": [{"name": "Red"}, {"name": "Blue"}]  // Reduce levels
       }
     ]
   }
   ```

3. **Monitor CPU usage:**
   ```bash
   top
   htop
   ```

4. **Check for infinite loops:**
   ```bash
   # Use timeout
   timeout 30 echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m conjoint_mcp.server
   ```

## Integration Issues

### Issue: Python Integration Problems
**Error:** `subprocess.TimeoutExpired` or connection issues

**Solutions:**
1. **Increase timeout:**
   ```python
   proc.communicate(input=line, timeout=60)  # Increase from 30
   ```

2. **Check server command:**
   ```python
   server_command = [sys.executable, "-m", "conjoint_mcp.server"]
   ```

3. **Handle errors gracefully:**
   ```python
   try:
       result = proc.communicate(input=line, timeout=30)
   except subprocess.TimeoutExpired:
       proc.kill()
       raise Exception("Server timeout")
   except Exception as e:
       raise Exception(f"Server error: {e}")
   ```

4. **Test server separately:**
   ```bash
   python -m conjoint_mcp.server
   ```

### Issue: JavaScript/Node.js Integration Problems
**Error:** `spawn` errors or communication issues

**Solutions:**
1. **Check Python path:**
   ```javascript
   const serverCommand = ['python', '-m', 'conjoint_mcp.server'];
   // Or use full path
   const serverCommand = ['/usr/bin/python3', '-m', 'conjoint_mcp.server'];
   ```

2. **Handle process errors:**
   ```javascript
   proc.on('error', (error) => {
       console.error('Failed to start server:', error);
       reject(error);
   });
   ```

3. **Add timeout handling:**
   ```javascript
   const timeout = setTimeout(() => {
       proc.kill();
       reject(new Error('Request timeout'));
   }, 30000);
   ```

4. **Test server separately:**
   ```bash
   python -m conjoint_mcp.server
   ```

## Error Codes Reference

### JSON-RPC Error Codes
| Code | Name | Description | Solution |
|------|------|-------------|----------|
| -32600 | Invalid Request | Malformed JSON-RPC request | Check JSON format and structure |
| -32601 | Method Not Found | Unknown method name | Verify method name spelling |
| -32602 | Invalid Params | Invalid or missing parameters | Check parameter structure and types |
| -32603 | Internal Error | Server internal error | Check server logs and restart |

### Application Error Codes
| Code | Name | Description | Solution |
|------|------|-------------|----------|
| -32000 | Server Error | Generic server error | Check server logs and restart |
| -32001 | Design Generation Error | Error in design generation | Check design parameters and complexity |
| -32002 | Constraint Violation Error | Constraint validation failed | Review constraint specifications |

### Common Error Messages
| Error | Cause | Solution |
|-------|-------|----------|
| "Field required" | Missing required parameter | Add missing parameter to request |
| "Invalid type" | Wrong parameter type | Check parameter data types |
| "Value too large" | Parameter value exceeds limit | Reduce parameter value |
| "Constraint violation" | Design violates constraints | Review and fix constraint specifications |

## Debugging Tools

### 1. Interactive Tester
```bash
python scripts/interactive_tester.py
```
- Step-by-step testing
- Real-time feedback
- Session history
- Error debugging

### 2. Local Test Suite
```bash
python scripts/local_test_suite.py
```
- Automated testing
- Performance benchmarking
- Error detection
- Comprehensive reporting

### 3. Performance Monitor
```bash
python scripts/performance_monitor.py --load-test 100
python scripts/performance_monitor.py --monitor 300
python scripts/performance_monitor.py --report
```
- Performance analysis
- Resource monitoring
- Load testing
- Performance reporting

### 4. Sample Scenarios
```bash
python scripts/sample_scenarios.py --list
python scripts/sample_scenarios.py --scenario clothing
```
- Pre-defined test scenarios
- Industry examples
- Constraint examples
- Validation scenarios

### 5. Debug Mode
```bash
export LOG_LEVEL=DEBUG
python -m conjoint_mcp.server
```
- Detailed logging
- Request/response tracking
- Performance metrics
- Error details

### 6. Manual Testing
```bash
# Test health
echo '{"jsonrpc": "2.0", "id": 1, "method": "health", "params": {}}' | python -m conjoint_mcp.server

# Test design generation
echo '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "design.generate",
  "params": {
    "method": "random",
    "grid": {
      "attributes": [
        {
          "name": "Color",
          "levels": [{"name": "Red"}, {"name": "Blue"}]
        }
      ]
    },
    "options_per_screen": 2,
    "num_screens": 3
  }
}' | python -m conjoint_mcp.server
```

## Getting Help

### 1. Check Documentation
- [API Documentation](api.md)
- [Usage Examples](examples.md)
- [Local Setup Guide](local_setup.md)

### 2. Use Debugging Tools
- Interactive tester
- Performance monitor
- Local test suite
- Sample scenarios

### 3. Check Logs
```bash
# Server logs
python -m conjoint_mcp.server 2>&1 | tee server.log

# Application logs
export LOG_LEVEL=DEBUG
python -m conjoint_mcp.server
```

### 4. Community Support
- GitHub Issues
- Documentation
- Examples
- Troubleshooting guides

### 5. Professional Support
- Enterprise support
- Training and consulting
- Custom development
- Performance optimization

## Prevention

### 1. Regular Testing
- Run health checks regularly
- Monitor performance metrics
- Test with sample scenarios
- Validate error handling

### 2. Proper Configuration
- Use appropriate timeouts
- Set reasonable limits
- Monitor resource usage
- Keep dependencies updated

### 3. Error Handling
- Implement retry logic
- Handle timeouts gracefully
- Validate inputs
- Log errors appropriately

### 4. Performance Monitoring
- Monitor response times
- Track memory usage
- Check CPU utilization
- Set up alerts

### 5. Documentation
- Document your designs
- Keep examples updated
- Maintain troubleshooting guides
- Share knowledge with team
