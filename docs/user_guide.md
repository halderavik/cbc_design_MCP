# CBC Design MCP - Complete User Guide

This guide shows you how to use the CBC Design MCP server with practical examples for different features and use cases.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Design Generation](#basic-design-generation)
3. [Advanced Features](#advanced-features)
4. [Export and File Management](#export-and-file-management)
5. [Statistical Optimization](#statistical-optimization)
6. [Real-World Examples](#real-world-examples)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Getting Started

### Prerequisites

- Claude Desktop or Cursor with MCP support
- CBC Design MCP server running locally or deployed

### Quick Setup

1. **Connect to Claude Desktop** (see `docs/claude_desktop_connection.md`)
2. **Connect to Cursor** (see `cursor_mcp_setup.md`)
3. **Test the connection** with a simple health check

### First Test

```
"Check if the CBC Design MCP is working by running a health check"
```

Expected response: The system should confirm the MCP is connected and working.

## Basic Design Generation

### Example 1: Simple Smartphone Design

**Prompt for ChatGPT:**
```
"Generate a CBC design for a smartphone with these attributes:
- Brand: Apple, Samsung, Google
- Storage: 64GB, 128GB, 256GB  
- Price: $299, $499, $699
- Camera: 12MP, 48MP, 108MP

Use the random algorithm and generate for 50 respondents."
```

**Expected ChatGPT Response:**
ChatGPT will automatically format this into the correct structure:
```json
{
  "spec": {
    "method": "random",
    "grid": {
      "attributes": [
        {"name": "Brand", "levels": [{"name": "Apple"}, {"name": "Samsung"}, {"name": "Google"}]},
        {"name": "Storage", "levels": [{"name": "64GB"}, {"name": "128GB"}, {"name": "256GB"}]},
        {"name": "Price", "levels": [{"name": "$299"}, {"name": "$499"}, {"name": "$699"}]},
        {"name": "Camera", "levels": [{"name": "12MP"}, {"name": "48MP"}, {"name": "108MP"}]}
      ]
    },
    "options_per_screen": 3,
    "num_screens": 10,
    "num_respondents": 50
  }
}
```

**What this does:**
- Creates a choice-based conjoint design
- 4 attributes with 3 levels each
- 50 respondents will see choice tasks
- Uses random assignment algorithm

### Example 2: Laptop Design with Optimal Sample Size

**Prompt:**
```
"Generate a CBC design for laptops with:
- Processor: Intel i5, Intel i7, AMD Ryzen 5, AMD Ryzen 7
- RAM: 8GB, 16GB, 32GB
- Storage: 256GB SSD, 512GB SSD, 1TB SSD
- Price: $799, $1199, $1599, $1999

Let the system suggest the optimal number of respondents."
```

**What this does:**
- 4 attributes with varying levels (4, 3, 3, 4 levels)
- System calculates optimal sample size using Johnson-Orme rule
- Automatically suggests 300 respondents (default commercial target)

### Example 3: Restaurant Menu Design

**Prompt:**
```
"Create a CBC design for restaurant menu items with:
- Cuisine: Italian, Mexican, Asian, American
- Price Range: $10-15, $15-20, $20-25, $25-30
- Rating: 3.5 stars, 4.0 stars, 4.5 stars
- Delivery Time: 20 min, 30 min, 45 min

Use the balanced overlap algorithm for 100 respondents."
```

## Advanced Features

### Example 4: D-Optimal Design for High-Quality Study

**Prompt:**
```
"Generate a high-quality CBC design for car purchases with:
- Brand: Toyota, Honda, Ford, BMW, Mercedes
- Fuel Type: Gasoline, Hybrid, Electric
- Price: $25k, $35k, $45k, $55k, $65k
- Warranty: 3 years, 5 years, 7 years

Use the D-optimal algorithm for maximum statistical efficiency."
```

**What this does:**
- Uses the most sophisticated algorithm
- Maximizes statistical efficiency (D-efficiency)
- Takes longer to generate but produces highest quality design
- Best for final studies and publications

### Example 5: Design with Constraints

**Prompt:**
```
"Generate a CBC design for hotel bookings with:
- Location: Downtown, Airport, Beach, Mountain
- Star Rating: 3-star, 4-star, 5-star
- Price: $100, $200, $300, $400
- Amenities: Basic, Premium, Luxury

Add constraints:
- 5-star hotels cannot be $100
- Beach locations cannot have Basic amenities
- Generate for 80 respondents using orthogonal arrays."
```

**What this does:**
- Applies business logic constraints
- Prevents unrealistic combinations
- Uses orthogonal arrays for balanced design
- Ensures statistical validity while respecting constraints

### Example 6: Multi-Respondent with Custom Tasks

**Prompt:**
```
"Generate a CBC design for streaming services with:
- Service: Netflix, Disney+, Amazon Prime, HBO Max
- Price: $8, $12, $15, $20
- Content: Movies, TV Shows, Sports, Documentaries
- Device Support: Mobile, TV, Computer, All Devices

Generate 15 choice tasks per respondent for 200 respondents using balanced overlap."
```

## Export and File Management

### Example 7: Export to CSV

**Prompt:**
```
"Export the last generated design to CSV format and save it as 'streaming_services_design.csv'"
```

**What this does:**
- Converts design to CSV format
- Includes respondent_ID, task, option, and attribute columns
- Saves file to your project directory
- Provides download link

### Example 8: Export to Qualtrics Format

**Prompt:**
```
"Export the design to Qualtrics format for easy survey import"
```

**What this does:**
- Creates Qualtrics-compatible format
- Includes proper question structure
- Ready for direct import into Qualtrics
- Includes metadata and instructions

### Example 9: Export with Preview

**Prompt:**
```
"Export the design to JSON format and show me a preview of the first 3 respondents' data"
```

**What this does:**
- Exports to JSON format
- Shows preview of data structure
- Helps verify design quality
- Useful for debugging and validation

## Statistical Optimization

### Example 10: Parameter Optimization

**Prompt:**
```
"Optimize the study parameters for a design with 5 attributes and 3 levels each, targeting 85% statistical power for main effects analysis."
```

**What this does:**
- Calculates optimal number of respondents
- Suggests optimal number of choice tasks
- Recommends alternatives per task
- Provides statistical power analysis

### Example 11: Sample Size Calculation

**Prompt:**
```
"Calculate the optimal sample size for a CBC study with:
- 4 attributes: 3, 4, 3, 2 levels
- 12 choice tasks per respondent
- 3 alternatives per task
- Need to detect main effects and 2-way interactions"
```

**What this does:**
- Uses Johnson-Orme rule-of-thumb
- Calculates for main effects and interactions
- Provides confidence intervals
- Suggests quality buffer for dropouts

### Example 12: Segment Analysis Planning

**Prompt:**
```
"Plan sample size for a CBC study that needs to analyze 3 market segments (young adults, families, seniors) with sufficient statistical power for each segment."
```

**What this does:**
- Calculates sample size per segment
- Ensures minimum 200 respondents per segment
- Provides total sample size recommendation
- Includes power analysis for segment comparisons

## Real-World Examples

### Example 13: E-commerce Product Design

**Prompt:**
```
"Generate a CBC design for an e-commerce website selling headphones with:
- Brand: Sony, Bose, Apple, Sennheiser
- Type: Over-ear, On-ear, In-ear, Wireless
- Price: $50, $150, $300, $500
- Features: Noise Cancelling, Waterproof, Long Battery, Premium Sound

Use D-optimal design for 300 respondents to support pricing strategy decisions."
```

**Business Use Case:** Pricing strategy, brand positioning, feature importance

### Example 14: Healthcare Service Design

**Prompt:**
```
"Create a CBC design for healthcare service preferences with:
- Provider Type: General Practitioner, Specialist, Nurse Practitioner
- Wait Time: Same day, 1 week, 2 weeks, 1 month
- Cost: $50, $100, $150, $200
- Location: Downtown, Suburb, Online, Home Visit

Generate for 400 respondents using balanced overlap to understand patient preferences."
```

**Business Use Case:** Service design, pricing optimization, resource allocation

### Example 15: Financial Product Design

**Prompt:**
```
"Design a CBC study for credit card preferences with:
- Annual Fee: $0, $50, $100, $200
- Rewards: Cash Back, Points, Miles, No Rewards
- APR: 12%, 16%, 20%, 24%
- Benefits: Travel Insurance, Purchase Protection, Extended Warranty, None

Use orthogonal arrays for 250 respondents to support product development."
```

**Business Use Case:** Product development, pricing strategy, feature prioritization

### Example 16: Transportation Service Design

**Prompt:**
```
"Generate a CBC design for ride-sharing service preferences with:
- Vehicle Type: Economy, Comfort, Premium, SUV
- Wait Time: 2 min, 5 min, 10 min, 15 min
- Price: $5, $10, $15, $20
- Driver Rating: 4.0, 4.5, 4.8, 5.0

Create for 350 respondents using balanced overlap to optimize service offerings."
```

**Business Use Case:** Service optimization, pricing strategy, market positioning

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Required fields missing: method and grid" (ChatGPT)
**Problem:** ChatGPT MCP wrapper expects specific payload structure
**Solution:**
```
"Generate a CBC design for [product] with [attributes] using [algorithm] for [X] respondents"
```
ChatGPT will automatically format this correctly. If it fails, try:
```
"Use generate_design with spec: {method: 'random', grid: {attributes: [list your attributes here]}, num_respondents: 50}"
```

#### Issue 2: "Design generation failed"
**Solution:**
```
"Try generating the design again with fewer attributes or levels, or use the random algorithm for faster generation."
```

#### Issue 3: "Sample size too small"
**Solution:**
```
"Optimize the parameters first to get the recommended sample size, then generate the design."
```

#### Issue 4: "Export failed"
**Solution:**
```
"Make sure you've generated a design first, then try exporting again."
```

#### Issue 5: "Constraints not working"
**Solution:**
```
"Check that your constraints are realistic and don't conflict with each other."
```

### Debugging Commands

**Check system status:**
```
"Run a health check to verify the MCP server is working properly"
```

**Validate design:**
```
"Show me the design statistics and efficiency metrics for the last generated design"
```

**Test with simple design:**
```
"Generate a simple 2-attribute design to test the system"
```

## Best Practices

### 1. Start Simple
- Begin with 2-3 attributes and 2-3 levels each
- Use random or balanced algorithms initially
- Test with small sample sizes first

### 2. Plan Your Study
- Define your research objectives clearly
- Choose appropriate attributes and levels
- Consider realistic constraints
- Plan for sufficient sample size

### 3. Choose the Right Algorithm
- **Random**: Fast testing and prototyping
- **Balanced**: General purpose studies
- **Orthogonal**: High-quality academic studies
- **D-Optimal**: Final studies and publications

### 4. Validate Your Design
- Check design efficiency metrics
- Review attribute level balance
- Verify constraints are working
- Test with a small sample first

### 5. Export and Save
- Always export your designs
- Save files with descriptive names
- Keep backups of important designs
- Document your study parameters

### 6. Sample Size Planning
- Use the optimization tool for guidance
- Consider your target segments
- Plan for dropouts and quality issues
- Balance statistical power with budget

## Advanced Tips

### Tip 1: Efficient Attribute Design
```
"Use 3-5 attributes with 2-4 levels each for optimal design efficiency"
```

### Tip 2: Realistic Constraints
```
"Add constraints that reflect real-world business rules and customer expectations"
```

### Tip 3: Segment Analysis
```
"Plan for 200+ respondents per segment if you need to analyze different customer groups"
```

### Tip 4: Quality Control
```
"Use D-optimal designs for final studies and publications to ensure maximum statistical efficiency"
```

### Tip 5: File Management
```
"Save designs with descriptive names including date, study type, and sample size"
```

## Example Workflow

Here's a complete workflow for a typical CBC study:

### Step 1: Planning
```
"Optimize parameters for a study with 4 attributes and 3 levels each, targeting 80% power for main effects"
```

### Step 2: Design Generation
```
"Generate a CBC design for [your product] with [your attributes] using the balanced algorithm for [recommended sample size] respondents"
```

### Step 3: Validation
```
"Show me the design efficiency metrics and attribute level balance"
```

### Step 4: Export
```
"Export the design to CSV format and save it as '[study_name]_design.csv'"
```

### Step 5: Documentation
```
"Provide a summary of the design parameters and recommendations for the survey implementation"
```

## Getting Help

If you encounter issues:

1. **Check the health status** of the MCP server
2. **Try simpler designs** to isolate the problem
3. **Review the error messages** for specific guidance
4. **Use the optimization tool** to validate your parameters
5. **Consult the troubleshooting section** above

## Conclusion

The CBC Design MCP provides powerful tools for creating high-quality choice-based conjoint studies. Start with simple designs, gradually add complexity, and always validate your results. The system's optimization tools and multiple algorithms ensure you can create studies that meet your specific research needs while maintaining statistical rigor.

Remember: Good CBC studies start with clear objectives, realistic attributes, and proper sample size planning. The MCP tools help you execute these studies efficiently and effectively.
