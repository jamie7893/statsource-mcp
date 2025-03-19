# Statsource MCP Server

Welcome to the **Statsource MCP Server**! This standalone server connects your AI agent (like Claude Desktop) to the Statsource API, allowing you to perform statistical calculations and data analysis. It’s easy to set up and works with your data, whether it’s in a PostgreSQL database or a CSV file.

## Features

- **Statistical Tools**: Calculate means, medians, standard deviations, and more.
- **Flexible Data Sources**: Supports PostgreSQL databases or CSV files.
- **Independent Operation**: Runs locally on your machine for maximum control.
- **Open-Source**: Customize it to fit your needs.

## Prerequisites

Before starting, ensure you have:

- **Python 3.8 or higher** installed.
- **Git** installed to download the repository.
- **An API key** from [https://statsource.me/](https://statsource.me/) (sign up to get yours).
- **(Optional)** A PostgreSQL database if you want to analyze database data.

## Installation

1. **Clone the Repository**  
   Download the code to your computer:

   ```bash
   git clone https://github.com/jamie7893/statsource-mcp.git
   cd statsource-mcp
   ```

2. **Set Up a Virtual Environment** (Recommended)  
   Create and activate a virtual environment to manage dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**  
   Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

To use the MCP server, you need to configure it with your specific settings. This involves setting the path to `mcp_server.py` and, if you’re using a PostgreSQL database, providing your database connection string.

### 1. Get Your API Key
- Sign up at [https://statsource.me/](https://statsource.me/) to get your API key.

### 2. Set Up MCP Configuration
- Your MCP configuration should look like this:

  ```json
  {
      "mcpServers": {
          "statsource": {
              "command": "python",
              "args": ["C:/Path/To/Statsource/mcp_server.py"],
              "env": {
                  "API_KEY": "your_api_key",
                  "DB_CONNECTION_STRING": "postgresql://postgres:postgres@localhost:5432/name_of_db",
                  "DB_SOURCE_TYPE": "database"
              }
          }
      }
  }
  ```

- **Update the Path**: Replace `"C:/Path/To/Statsource/mcp_server.py"` with the actual path to `mcp_server.py` on your computer. For example, if you cloned the repo to `D:/Projects/statsource-mcp`, the path might be `"D:/Projects/statsource-mcp/mcp_server.py"`.
- **API Key**: Replace `"your_api_key"` with the key you got from [https://statsource.me/](https://statsource.me/).
- **Database Connection (Optional)**: If you’re using a PostgreSQL database, update `"postgresql://postgres:postgres@localhost:5432/name_of_db"` with your database connection string (e.g., username, password, host, port, and database name). If you’re not using a database, remove `"DB_CONNECTION_STRING"` and `"DB_SOURCE_TYPE"`.

> **Note**: The exact configuration depends on your Python version and where you installed the repository. Adjust the paths and settings as needed.

## Running the Server

Once configured, start the server:

```bash
python mcp_server.py
```

The server uses standard input/output, making it compatible with AI agents like Claude Desktop.

## Available Tools

### get_statistics
Analyze data and calculate statistics or generate ML predictions based on provided parameters.

#### What this tool does:
This tool connects to our analytics API and provides two main functionalities:
1. Statistical Analysis: Calculate various statistical measures on specified data columns
2. ML Predictions: Generate time-series forecasts for future periods based on historical data

#### Important Instructions for AI Agents:
- DO NOT make up or guess any parameter values, especially data sources or column names
- NEVER, UNDER ANY CIRCUMSTANCES, create or invent database connection strings - this is a severe security risk
- ALWAYS ask the user explicitly for all required information
- For CSV files: The user MUST first upload their file to statsource.me, then provide the filename
- For database connections: Ask the user for their exact PostgreSQL connection string - DO NOT MODIFY IT
- Never suggest default values, sample data, or example parameters - request specific information from the user
- If the user has configured a default database connection in their MCP config, inform them it will be used if they don't specify a data source
- If no database connection is provided in the MCP config and the user doesn't provide one, DO NOT PROCEED - ask user to provide connection details

#### When to use this tool:
- When a user needs statistical analysis of their data (means, medians, etc.)
- When a user wants to predict future values based on historical trends
- When analyzing trends, patterns, or distributions in datasets
- When generating forecasts for business planning or decision-making

#### Required inputs:
- columns: List of column names to analyze or predict (ask user for exact column names in their data)

#### Optional inputs:
- data_source: Path to data file, database connection string, or API endpoint
  * For CSV: Filename of a previously uploaded file on statsource.me (ask user to upload first)
  * For Database: Full connection string (ask user for exact string)
  * If not provided, will use the connection string from MCP config if available
- source_type: Type of data source ("csv", "database", or "api")
  * If not provided, will use the source type from MCP config if available
- statistics: List of statistics to calculate (only required for statistical analysis)
- query_type: Type of query ("statistics" or "ml_prediction")
- periods: Number of future periods to predict (only used for ML predictions)

#### Valid statistics options:
- Basic (free tier): "mean", "median", "min", "max", "count", "sum", "std", "var"
- Advanced (paid tier): "skewness", "kurtosis", "percentile", "histogram", "correlation"

#### ML Prediction features:
- Time series forecasting with customizable prediction periods
- Trend direction analysis ("increasing", "decreasing", "stable")
- Model quality metrics (r-squared, slope)
- Works with numeric data columns from any supported data source

#### Returns:
For statistics queries:
- Statistical measures for each requested column and statistic

For ML prediction queries:
- Predicted future values for specified columns
- Trend direction and model quality metrics
- R-squared value and slope indicators

#### Example questions to ask users:
1. "Have you already uploaded your CSV file to statsource.me? What is the filename?"
2. "What is your exact PostgreSQL connection string?" (if not configured in MCP config)
3. "Which specific columns in your data would you like to analyze?"
4. "Which statistics would you like to calculate for these columns?"
5. "How many future periods would you like to predict?"

#### Configuration:
Users can set a default database connection string in their MCP config:
```json
{
  "mcpServers": {
    "statsource": {
      "command": "python",
      "args": ["path/to/mcp_server.py"],
      "env": {
        "API_KEY": "your_api_key",
        "DB_CONNECTION_STRING": "postgresql://username:password@localhost:5432/your_db",
        "DB_SOURCE_TYPE": "database"
      }
    }
  }
}
```

## Troubleshooting

- **Command Not Found**: Ensure you’re in the virtual environment (`source venv/bin/activate` or `venv\Scripts\activate`) and the path to `mcp_server.py` is correct.
- **API Errors**: Double-check your API key and internet connection.
- **Database Issues**: Verify your PostgreSQL database is running and the connection string is correct.

For more help, check the [official documentation](#).

