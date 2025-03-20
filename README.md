# Statsource MCP Server
A Model Context Protocol server that provides statistical analysis capabilities. This server enables LLMs to analyze data from various sources, calculate statistics, and generate predictions.

The statistics tool connects to our analytics API and allows AI models to perform statistical analysis and generate ML predictions based on user data, whether it's in a PostgreSQL database or a CSV file.

## Available Tools

### get_statistics
Analyze data and calculate statistics or generate ML predictions based on provided parameters.

**Arguments:**
- `columns` (list of strings, required): List of column names to analyze or predict
- `data_source` (string, optional): Path to data file, database connection string, or API endpoint
- `source_type` (string, optional): Type of data source ("csv", "database", or "api")
- `statistics` (list of strings, optional): List of statistics to calculate (for statistical analysis)
- `query_type` (string, optional): Type of query ("statistics" or "ml_prediction")
- `periods` (integer, optional): Number of future periods to predict (for ML predictions)

### suggest_feature
Suggest a new feature or improvement for the StatSource analytics platform.

**Arguments:**
- `description` (string, required): A clear, detailed description of the suggested feature
- `use_case` (string, required): Explanation of how and why users would use this feature
- `priority` (string, optional): Suggested priority level ("low", "medium", "high")

## Installation

### Using uv (recommended)
When using uv no specific installation is needed. We will use uvx to directly run mcp-server-stats.

### Using PIP
Alternatively you can install mcp-server-stats via pip:

```bash
pip install mcp-server-stats
```

After installation, you can run it as a script using:

```bash
python -m mcp_server_stats
```

Or use the console script:

```bash
mcp-server-stats
```

## Configuration

### Configure for Claude.app
Add to your Claude settings:

**Using uvx**
```json
"mcpServers": {
  "statsource": {
    "command": "uvx",
    "args": ["mcp-server-stats"]
  }
}
```

**Using docker**
```json
"mcpServers": {
  "statsource": {
    "command": "docker",
    "args": ["run", "-i", "--rm", "statsource/mcp"]
  }
}
```

**Using pip installation**
```json
"mcpServers": {
  "statsource": {
    "command": "python",
    "args": ["-m", "mcp_server_stats"]
  }
}
```

### Environment Variables

You can configure the server using environment variables in your Claude.app configuration:

```json
"mcpServers": {
  "statsource": {
    "command": "python",
    "args": ["-m", "mcp_server_stats"],
    "env": {
      "API_KEY": "your_api_key",
      "DB_CONNECTION_STRING": "postgresql://username:password@localhost:5432/your_db",
      "DB_SOURCE_TYPE": "database"
    }
  }
}
```

Available environment variables:

- `API_KEY`: Your API key for authentication with statsource.me
- `DB_CONNECTION_STRING`: Default database connection string 
- `DB_SOURCE_TYPE`: Default data source type (usually "database")

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```bash
npx @modelcontextprotocol/inspector uvx mcp-server-stats
```

Or if you've installed the package in a specific directory or are developing on it:

```bash
cd path/to/servers/
npx @modelcontextprotocol/inspector python -m mcp_server_stats
```

## Contributing

We encourage contributions to help expand and improve mcp-server-stats. Whether you want to add new tools, enhance existing functionality, or improve documentation, your input is valuable.

Pull requests are welcome! Feel free to contribute new ideas, bug fixes, or enhancements to make mcp-server-stats even more powerful and useful.

## License

mcp-server-stats is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.

