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
   git clone https://github.com/yourusername/statsource-mcp.git
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

## Troubleshooting

- **Command Not Found**: Ensure you’re in the virtual environment (`source venv/bin/activate` or `venv\Scripts\activate`) and the path to `mcp_server.py` is correct.
- **API Errors**: Double-check your API key and internet connection.
- **Database Issues**: Verify your PostgreSQL database is running and the connection string is correct.

For more help, check the [official documentation](#).

