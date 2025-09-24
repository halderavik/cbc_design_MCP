# CBC Design Generator MCP Server

A comprehensive Model Context Protocol (MCP) server for generating Choice Based Conjoint (CBC) designs with advanced statistical optimization and multi-respondent support.

## 🚀 Features

- **4 Design Algorithms**: Random, Balanced Overlap, Orthogonal Arrays, and D-Optimal designs
- **Automatic Respondent Optimization**: Statistical power analysis for optimal sample sizes
- **Multi-Respondent Support**: Generate designs for all respondents with `respondent_ID` column
- **Multiple Export Formats**: CSV, JSON, and Qualtrics-compatible formats
- **File Saving**: Direct file export to project directory
- **Constraint Management**: Support for prohibited/required combinations and level balance
- **Statistical Validation**: D-efficiency calculations and design quality metrics

## 📋 Available MCP Tools

1. **`generate_design`** - Generate CBC designs with 4 algorithms
2. **`optimize_parameters`** - Optimize study parameters for statistical power
3. **`export_design`** - Export designs in multiple formats with preview
4. **`save_design_file`** - Save complete design files to disk

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation

1. **Clone and navigate to the repository:**
   ```bash
   git clone <repository-url>
   cd CBC_design_MCP
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

4. **Copy environment file:**
   ```bash
   copy .env.example .env
   ```

## 🏃‍♂️ Running the Server

### Local Development
```bash
python -m conjoint_mcp.mcp_server_v2
```

### With Claude Desktop
1. **Configure Claude Desktop** (`claude_desktop_config.json`):
   ```json
   {
     "mcpServers": {
       "cbc-design-generator": {
         "command": "python",
         "args": ["-m", "conjoint_mcp.mcp_server_v2"],
         "cwd": "C:\\path\\to\\CBC_design_MCP",
         "env": {
           "PYTHONPATH": "C:\\path\\to\\CBC_design_MCP\\src",
           "LOG_LEVEL": "WARNING"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop** to load the MCP server

### With Cursor
1. **Configure Cursor** (`.cursor/mcp.json`):
   ```json
   {
     "mcpServers": {
       "cbc-design-generator": {
         "command": "python",
         "args": ["-m", "conjoint_mcp.mcp_server_v2"],
         "cwd": "C:\\path\\to\\CBC_design_MCP",
         "env": {
           "PYTHONPATH": "C:\\path\\to\\CBC_design_MCP\\src",
           "LOG_LEVEL": "WARNING"
         }
       }
     }
   }
   ```

## 📖 Usage Examples

### Generate a Design
```
"Generate a CBC design for a smartphone with brand, storage, and price attributes using the random algorithm"
```

### Optimize Parameters
```
"Optimize study parameters for a design with 3 attributes and 3 levels each, targeting 80% statistical power"
```

### Export and Save
```
"Export the design to CSV and save it as 'smartphone_survey_design'"
```

### Generate with Optimal Sample Size (Default)
```
"Generate a CBC design with laptop attributes: processor, storage, display, and price"
```
*The system automatically suggests the optimal number of respondents based on statistical power analysis*

### Generate with Specific Respondents
```
"Generate a CBC design for 100 respondents with laptop attributes: processor, storage, display, and price"
```

## 📊 Output Formats

### CSV Export Structure
```csv
respondent_ID,Task_Index,Option_Index,Attribute1,Attribute2,Attribute3
1,1,1,Level1,Level2,Level3
1,1,2,Level4,Level5,Level6
...
2,1,1,Level1,Level2,Level3
...
```

### Design Algorithms

| Algorithm | Speed | Efficiency | Use Case |
|-----------|-------|------------|----------|
| **Random** | Very Fast | Low-Moderate | Testing, Prototyping |
| **Balanced** | Fast | Moderate | General Purpose |
| **Orthogonal** | Moderate | High | High-Quality Studies |
| **D-Optimal** | Slow | Highest | Final Studies |

## 🧪 Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/unit/test_performance.py
```

### Test Coverage
```bash
pytest --cov=src/conjoint_mcp
```

## 🧠 Johnson-Orme Sample Size Calculation

The MCP server uses the academically validated Johnson-Orme rule-of-thumb for CBC sample size calculation:

### **Johnson-Orme Formula**
- **Main Effects**: n ≥ 500c / (t × a)
- **With Interactions**: n ≥ 500c / (t × a) where c = largest product of attribute levels
- **Quality Buffer**: +15% for dropouts and quality loss

Where:
- **n** = respondents
- **t** = choice tasks per respondent
- **a** = alternatives per task
- **c** = largest number of levels for any attribute (main effects)
- **c** = largest product of levels for any attribute pair (interactions)

### **Example Calculations**
- **Laptop design** (4 attributes × 3 levels, 12 tasks, 3 alts): 49 respondents (main effects)
- **With interactions**: 144 respondents
- **Conservative (1000×)**: 97 respondents (main effects)

### **Pragmatic Targets**
- **Minimum credible**: 250 respondents
- **Typical commercial**: 300 respondents  
- **Subgroup analysis**: 400+ respondents
- **High precision**: Use 1000× multiplier

### **Why This Works**
- Based on peer-reviewed academic literature
- Validated across thousands of CBC studies
- Accounts for design efficiency and statistical power
- Includes practical considerations for real-world studies

### **Override When Needed**
You can always specify a custom number of respondents:
```
"Generate a CBC design for 100 respondents with [your attributes]"
```

## 🔧 Development

### Code Quality Tools
```bash
# Install pre-commit hooks
pre-commit install

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Project Structure
```
src/conjoint_mcp/
├── algorithms/          # Design generation algorithms
├── constraints/         # Constraint management
├── handlers/           # Request handlers
├── models/             # Pydantic models
├── utils/              # Utility functions
└── mcp_server_v2.py    # Main MCP server
```

## 📚 Documentation

- **API Documentation**: `docs/api.md`
- **Usage Examples**: `docs/examples.md`
- **Algorithm Details**: `docs/algorithms.md`
- **Troubleshooting**: `docs/troubleshooting.md`
- **Deployment Guide**: `docs/deployment.md`

## 🚀 Deployment

### Heroku
This repo includes `Procfile` and `runtime.txt`. Set environment variables via Heroku config vars.

### Docker
```bash
docker build -t cbc-design-generator .
docker run -p 8000:8000 cbc-design-generator
```

## 📈 Performance

- **Random Algorithm**: < 1 second for 1000 respondents
- **Balanced Algorithm**: < 2 seconds for 1000 respondents  
- **Orthogonal Algorithm**: < 5 seconds for 1000 respondents
- **D-Optimal Algorithm**: < 30 seconds for 1000 respondents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Check the `docs/` directory for detailed guides
- **Examples**: See `docs/examples.md` for usage examples



