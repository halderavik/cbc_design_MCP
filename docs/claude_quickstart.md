# Claude Desktop Quickstart: CBC Design Generator MCP

This guide assumes Claude Desktop is already connected to the MCP server (`conjoint_mcp.mcp_server_v2`). Copy the prompts below directly into Claude to exercise every capability quickly.

## 1) Verify Connection and Discover Tools
- Prompt:
```
List the tools available from the CBC Design Generator and briefly describe each.
```

Expected: You should see `generate_design`, `optimize_parameters`, `export_design`, and `save_design_file` with schemas.

## 2) Generate a Simple Design (Random)
- Prompt:
```
Use the CBC Design Generator to generate a random CBC design with:
- Attributes:
  - Color: Red, Blue
  - Size: S, L
- Options per screen: 2
- Number of screens: 3
Return the design summary.
```

Notes:
- If `num_respondents` is omitted, the server defaults to 300 respondents (commercial standard).
- For segment analysis, specify custom sample size or segments for precise calculations.

## 3) Optimize Study Parameters
- Prompt:
```
Optimize the study parameters for a grid with 3 attributes and 3 levels each targeting 80% power. Show the recommended respondents, number of screens, and options per screen.
```

Expected: You’ll receive a recommended design size with an expected power value.

## 4) Generate a Laptop Study (D-Optimal)
- Prompt:
```
Generate a CBC design using the D-optimal method for this laptop study:
- Attributes and levels:
  - Processor & RAM: Intel Core i5 / 8GB RAM; Intel Core i7 / 16GB RAM; Intel Core i9 / 32GB RAM
  - Storage: 256GB SSD; 512GB SSD; 1TB SSD
  - Display: 13-inch, Full HD (1920x1080); 14-inch, 2K (2560x1440); 16-inch, 4K OLED (3840x2160)
  - Price: $999; $1,499; $2,199
- Options per screen: 3
- Number of screens: 12
Return a summary with efficiency and total observations.
```

## 5) Export the Latest Design to CSV (Preview)
- Prompt:
```
Export the most recently generated design to CSV. Show a short preview (first 1000 characters) and a summary of the columns.
```

Expected:
- Preview content
- CSV structure explanation
- `respondent_ID` column present

## 6) Save the Full CSV to Disk
- Option A (via export tool with auto-save):
```
Export the most recently generated design to CSV and save it to a file with filename "laptop_survey_design". Tell me the full file path.
```

- Option B (via dedicated save tool):
```
Save the most recently generated design to a CSV file named "laptop_survey_design" and report the full path and file size.
```

Result: A `.csv` file is written to your project directory with all respondents × tasks × options.

## 7) Export to JSON
- Prompt:
```
Export the most recently generated design to JSON and save it as "laptop_survey_design_json". Provide the file path and a short content preview.
```

## 8) Explore Server Resources (Catalog)
- Prompt:
```
List the resources available from the CBC Design Generator server, and then read the content for algorithms and examples.
```

Expected: A JSON list of algorithms and sample scenarios the server publishes.

## 9) Validate Constraint Awareness (Optional)
- Prompt:
```
Export the latest design to CSV while checking this prohibited combination:
- Prohibited: { "Processor & RAM": "Intel Core i5 / 8GB RAM", "Display": "16-inch, 4K OLED (3840x2160)" }
Show any violations found.
```

## Troubleshooting Tips
- If Claude can’t see the tools, restart Claude Desktop to reload MCP servers.
- Ensure your config points to `conjoint_mcp.mcp_server_v2` and `PYTHONPATH` includes the `src` directory.
- Large designs may be previewed in the chat, but saved fully to disk when you request saving.

## Where Files Are Saved
By default, files are saved in your project root directory:
```
C:\Users\<you>\my_dev\CBC_design_MCP\
```
(Claude will confirm the exact path after saving.)
