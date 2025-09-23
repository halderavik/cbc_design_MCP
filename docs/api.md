# CBC Design Generator MCP Server - API Documentation

This document provides comprehensive API documentation for the CBC Design Generator MCP Server, including all available methods, request/response formats, error codes, and usage examples.

## Table of Contents

1. [Overview](#overview)
2. [JSON-RPC Protocol](#json-rpc-protocol)
3. [Available Methods](#available-methods)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Examples](#examples)
7. [Performance Considerations](#performance-considerations)

## Overview

The CBC Design Generator MCP Server implements the Model Context Protocol (MCP) using JSON-RPC 2.0 for communication. It provides methods for generating Choice Based Conjoint (CBC) designs, optimizing study parameters, and exporting results.

### Base URL
- **Stdio Mode**: `python -m conjoint_mcp.server`
- **HTTP Mode**: `http://localhost:8080` (if implemented)

### Protocol
- **JSON-RPC Version**: 2.0
- **Content-Type**: `application/json`
- **Communication**: Request/Response over stdio or HTTP

## JSON-RPC Protocol

### Request Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "method.name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

### Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "field1": "value1",
    "field2": "value2"
  }
}
```

### Error Response Format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": {
      "additional": "error details"
    }
  }
}
```

## Available Methods

### 1. Health Check

#### `ping` / `health`
Check server health and status.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "health",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "ok",
    "version": "0.1.0"
  }
}
```

**Parameters:** None

**Returns:**
- `status` (string): Server status ("ok")
- `version` (string): Server version

---

### 2. Design Generation

#### `design.generate`
Generate a CBC design using specified algorithm and parameters.

**Request:**
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
          "levels": [
            {"name": "Red"},
            {"name": "Blue"},
            {"name": "Green"}
          ]
        },
        {
          "name": "Size",
          "levels": [
            {"name": "S"},
            {"name": "M"},
            {"name": "L"}
          ]
        }
      ]
    },
    "options_per_screen": 3,
    "num_screens": 10,
    "constraints": {
      "prohibited_combinations": [
        {
          "attributes": {"Color": "Red", "Size": "S"},
          "reason": "Red small items not available"
        }
      ]
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tasks": [
      {
        "task_index": 1,
        "options": [
          {"Color": "Blue", "Size": "M"},
          {"Color": "Green", "Size": "L"},
          {"Color": "Red", "Size": "M"}
        ]
      },
      {
        "task_index": 2,
        "options": [
          {"Color": "Green", "Size": "S"},
          {"Color": "Blue", "Size": "L"},
          {"Color": "Red", "Size": "S"}
        ]
      }
    ],
    "efficiency": 0.75,
    "notes": "Design generated successfully"
  }
}
```

**Parameters:**
- `method` (string, required): Algorithm name ("random", "balanced", "orthogonal", "doptimal")
- `grid` (object, required): Design grid specification
  - `attributes` (array, required): List of attributes with levels
- `options_per_screen` (integer, optional): Number of options per choice task (default: 3)
- `num_screens` (integer, optional): Number of choice tasks (default: 10)
- `constraints` (object, optional): Constraint specification

**Returns:**
- `tasks` (array): List of choice tasks
- `efficiency` (number): Design efficiency score (0-1)
- `notes` (string, optional): Additional information

---

### 3. Parameter Optimization

#### `design.optimize`
Optimize design parameters based on statistical requirements.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "design.optimize",
  "params": {
    "grid": {
      "attributes": [
        {
          "name": "Color",
          "levels": [
            {"name": "Red"},
            {"name": "Blue"}
          ]
        },
        {
          "name": "Size",
          "levels": [
            {"name": "S"},
            {"name": "L"}
          ]
        }
      ]
    },
    "target_power": 0.8,
    "effect_size": 0.2,
    "alpha": 0.05,
    "max_respondents": 1000,
    "max_screens": 20,
    "max_options": 5
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "num_respondents": 200,
    "num_screens": 12,
    "options_per_screen": 3,
    "expected_power": 0.82,
    "parameter_count": 4,
    "design_complexity": 4,
    "notes": "Optimization completed successfully"
  }
}
```

**Parameters:**
- `grid` (object, required): Design grid specification
- `target_power` (number, optional): Target statistical power (default: 0.8)
- `effect_size` (number, optional): Expected effect size (default: 0.2)
- `alpha` (number, optional): Significance level (default: 0.05)
- `max_respondents` (integer, optional): Maximum number of respondents (default: 1000)
- `max_screens` (integer, optional): Maximum number of screens (default: 20)
- `max_options` (integer, optional): Maximum options per screen (default: 5)

**Returns:**
- `num_respondents` (integer): Recommended number of respondents
- `num_screens` (integer): Recommended number of screens
- `options_per_screen` (integer): Recommended options per screen
- `expected_power` (number): Expected statistical power
- `parameter_count` (integer): Number of parameters to estimate
- `design_complexity` (integer): Design complexity score
- `notes` (string, optional): Additional information

---

### 4. Design Export

#### `design.export`
Export generated design in specified format.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "design.export",
  "params": {
    "design_request": {
      "method": "random",
      "grid": {
        "attributes": [
          {
            "name": "Color",
            "levels": [
              {"name": "Red"},
              {"name": "Blue"}
            ]
          }
        ]
      },
      "options_per_screen": 3,
      "num_screens": 5
    },
    "format": "csv",
    "include_metadata": true,
    "constraints": {
      "prohibited_combinations": []
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": "# CBC Design Export\n# Generated by CBC Design Generator MCP Server\n# Efficiency Score: 0.75\n\nTask_Index,Option_Index,Color\n1,1,Red\n1,2,Blue\n1,3,Red\n2,1,Blue\n2,2,Red\n2,3,Blue",
    "format": "csv",
    "summary": {
      "total_tasks": 5,
      "total_options": 15,
      "average_options_per_task": 3.0,
      "attributes": ["Color"],
      "attribute_levels": {
        "Color": ["Blue", "Red"]
      },
      "efficiency_score": 0.75,
      "notes": null
    },
    "validation_results": {
      "is_valid": true,
      "violations": [],
      "constraint_summary": {
        "prohibited_combinations": 0,
        "required_combinations": 0,
        "level_balance_constraints": 0,
        "custom_rules": 0
      }
    }
  }
}
```

**Parameters:**
- `design_request` (object, required): Original design generation request
- `format` (string, optional): Export format ("csv", "json", "qualtrics") (default: "csv")
- `include_metadata` (boolean, optional): Include metadata in export (default: true)
- `constraints` (object, optional): Constraint specification for validation

**Returns:**
- `content` (string): Exported content
- `format` (string): Export format used
- `summary` (object): Design summary statistics
- `validation_results` (object, optional): Constraint validation results

## Data Models

### DesignGrid
```json
{
  "attributes": [
    {
      "name": "string",
      "levels": [
        {"name": "string"}
      ]
    }
  ]
}
```

### Attribute
```json
{
  "name": "string",
  "levels": [
    {"name": "string"}
  ]
}
```

### AttributeLevel
```json
{
  "name": "string"
}
```

### ConstraintSpec
```json
{
  "prohibited_combinations": [
    {
      "attributes": {"string": "string"},
      "reason": "string"
    }
  ],
  "required_combinations": [
    {
      "attributes": {"string": "string"},
      "reason": "string"
    }
  ],
  "level_balance_constraints": [
    {
      "attribute_name": "string",
      "min_frequency": 0,
      "max_frequency": 100,
      "tolerance": 0.1
    }
  ],
  "custom_rules": [
    {
      "name": "string",
      "condition": "string",
      "action": "string",
      "description": "string"
    }
  ],
  "max_complexity": 10
}
```

## Error Handling

### Error Codes

| Code | Name | Description |
|------|------|-------------|
| -32600 | Invalid Request | The JSON sent is not a valid Request object |
| -32601 | Method Not Found | The method does not exist / is not available |
| -32602 | Invalid Params | Invalid method parameter(s) |
| -32603 | Internal Error | Internal JSON-RPC error |
| -32000 | Server Error | Generic server error |
| -32001 | Design Generation Error | Error in design generation process |
| -32002 | Constraint Violation Error | Constraint validation failed |

### Error Response Examples

#### Method Not Found
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found: invalid.method"
  }
}
```

#### Invalid Parameters
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Invalid parameters for design generation",
    "data": {
      "validation_errors": [
        {
          "type": "missing",
          "loc": ["grid", "attributes"],
          "msg": "Field required"
        }
      ]
    }
  }
}
```

#### Constraint Violation
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32002,
    "message": "Constraint validation failed",
    "data": {
      "violations": [
        "Task 1: Prohibited combination: {'Color': 'Red', 'Size': 'S'}"
      ]
    }
  }
}
```

## Examples

### Basic Design Generation
```bash
# Generate a simple random design
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
    "options_per_screen": 3,
    "num_screens": 5
  }
}' | python -m conjoint_mcp.server
```

### Parameter Optimization
```bash
# Optimize parameters for a design
echo '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "design.optimize",
  "params": {
    "grid": {
      "attributes": [
        {
          "name": "Brand",
          "levels": [{"name": "A"}, {"name": "B"}, {"name": "C"}]
        },
        {
          "name": "Price",
          "levels": [{"name": "$10"}, {"name": "$20"}, {"name": "$30"}]
        }
      ]
    },
    "target_power": 0.8,
    "effect_size": 0.2
  }
}' | python -m conjoint_mcp.server
```

### Design Export
```bash
# Export design to CSV format
echo '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "design.export",
  "params": {
    "design_request": {
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
      "num_screens": 5
    },
    "format": "csv"
  }
}' | python -m conjoint_mcp.server
```

## Performance Considerations

### Response Times
- **Health Check**: < 100ms
- **Random Design**: < 1s
- **Balanced Design**: < 2s
- **Orthogonal Design**: < 2s
- **D-Optimal Design**: < 10s (depends on complexity)
- **Parameter Optimization**: < 5s
- **Export**: < 1s

### Memory Usage
- **Base Memory**: ~50MB
- **Per Design**: ~1MB per 100 tasks
- **Maximum Recommended**: 500MB for large designs

### Scalability Limits
- **Maximum Attributes**: 10
- **Maximum Levels per Attribute**: 10
- **Maximum Screens**: 50
- **Maximum Options per Screen**: 10
- **Maximum Respondents**: 10,000

### Best Practices
1. **Use appropriate algorithms** for your needs:
   - Random: Fastest, good for testing
   - Balanced: Good balance of speed and quality
   - Orthogonal: Best for orthogonal designs
   - D-Optimal: Best statistical properties, slower

2. **Optimize parameters** before generating large designs
3. **Use constraints** to improve design quality
4. **Monitor performance** with the performance monitor
5. **Export results** for external analysis

## Rate Limiting

Currently, no rate limiting is implemented. For production use, consider implementing:
- Request rate limiting (requests per minute)
- Concurrent request limiting
- Resource usage monitoring
- Automatic scaling based on load

## Security Considerations

1. **Input Validation**: All inputs are validated using Pydantic
2. **Error Handling**: Sensitive information is not exposed in error messages
3. **Resource Limits**: Memory and CPU usage are monitored
4. **Logging**: Request logging excludes sensitive data

## Versioning

The API follows semantic versioning (SemVer):
- **Major version**: Breaking changes
- **Minor version**: New features, backward compatible
- **Patch version**: Bug fixes, backward compatible

Current version: 0.1.0

## Support

For API support:
- Check the troubleshooting guide
- Review error messages and codes
- Use the interactive tester for debugging
- Monitor performance metrics
