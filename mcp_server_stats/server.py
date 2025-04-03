"""
MCP (Message Control Protocol) Server for Statistical Analysis

This module implements an MCP server that acts as a middleware between
clients (like Claude Desktop app) and our existing API. It runs independently
and forwards requests to the API whose URL is configurable via environment variables.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field, field_validator
from mcp.server.fastmcp import FastMCP
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_server_stats")

# Read API location from environment variable with a default fallback
API_URL = "https://api.statsource.me"
API_KEY = os.getenv("API_KEY", None)  # Optional API key for authentication
# Database connection string from environment variable
DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING", None)
DB_SOURCE_TYPE = os.getenv("DB_SOURCE_TYPE", "database")  # Default to database if not specified

# Initialize MCP server
mcp = FastMCP("ai_mcp_server")

# Define input models for data validation
class StatisticsRequest(BaseModel):
    """Request model for statistical operations."""
    operation: str = Field(..., description="Statistical operation to perform (mean, median, sum, etc.)")
    data: List[float] = Field(..., description="List of numeric data points")
    
    @field_validator('operation')
    @classmethod
    def validate_operation(cls, v):
        valid_operations = ['mean', 'median', 'sum', 'min', 'max', 'std', 'var', 'count']
        if v.lower() not in valid_operations:
            raise ValueError(f"Operation must be one of {valid_operations}")
        return v.lower()
    
    @field_validator('data')
    @classmethod
    def validate_data(cls, v):
        if not v:
            raise ValueError("Data list cannot be empty")
        return v

# Helper function to check if API is available
def is_api_available() -> bool:
    """
    Check if the API is available.
    
    Returns:
        bool: True if API is available, False otherwise
    """
    try:
        # Try to connect to the base URL
        response = requests.get(API_URL, timeout=5)
        return response.status_code < 500  # Consider 2xx, 3xx, 4xx as "available"
    except requests.RequestException:
        return False

# Helper function to make API calls
def call_api(endpoint: str, data: Dict[str, Any], params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Make a request to the API.
    
    Args:
        endpoint: API endpoint path (without base URL)
        data: Request payload
        params: URL query parameters
        
    Returns:
        API response as dictionary
    
    Raises:
        Exception: If the API request fails
    """
    # Check if API is available first
    if not is_api_available():
        raise Exception(f"API at {API_URL} is not available")
    
    headers = {"Content-Type": "application/json"}
    
    # Add authentication if API key is provided
    if API_KEY:
        headers["API-Key"] = API_KEY
    
    try:
        logger.info(f"Calling API endpoint: {endpoint}")
        response = requests.post(f"{API_URL}{endpoint}", json=data, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            error_text = e.response.text
            status_code = e.response.status_code
            return {"error": f"API request failed with status {status_code}: {error_text}"}
        else:
            error_text = str(e)
            return {"error": f"API request failed: {error_text}"}

# Define MCP tools
@mcp.tool()
def suggest_feature(description: str, use_case: str, priority: str = "medium") -> str:
    """
    Suggest a new feature or improvement for the StatSource analytics platform.
    
    ### What this tool does:
    This tool allows you to submit feature suggestions or enhancement requests for 
    the StatSource platform. Suggestions are logged and reviewed by the development team.
    
    ### When to use this tool:
    - When a user asks for functionality that doesn't currently exist
    - When you identify gaps or limitations in the current analytics capabilities
    - When a user expresses frustration about missing capabilities
    - When you think of enhancements that would improve the user experience
    
    ### Required inputs:
    - description: A clear, detailed description of the suggested feature
    - use_case: Explanation of how and why users would use this feature
    
    ### Optional inputs:
    - priority: Suggested priority level ("low", "medium", "high")
    
    ### Returns:
    A confirmation message and reference ID for the feature suggestion.
    """
    try:
        # Format the request
        suggestion_data = {
            "description": description,
            "use_case": use_case,
            "priority": priority,
            "source": "ai_agent"
        }
        
        # Call the feature suggestion endpoint
        endpoint = "/api/v1/feature_suggestions"
        response = call_api(endpoint, suggestion_data)
        
        if "error" in response:
            return f"Error: {response['error']}"
        
        # Format the response
        suggestion_id = response.get("id", "unknown")
        return json.dumps({
            "status": "received",
            "message": "Thank you for your feature suggestion. Our team will review it.",
            "suggestion_id": f"FEAT-{suggestion_id}"
        }, indent=2)
    except Exception as e:
        return f"Error submitting feature suggestion: {str(e)}"

@mcp.tool()
def get_statistics(data_source: Optional[str] = None, source_type: Optional[str] = None, table_name: Optional[str] = None, columns: List[str] = [], statistics: Optional[List[str]] = None, query_type: str = "statistics", periods: Optional[int] = None, filters: Optional[Dict[str, Any]] = None, groupby: Optional[List[str]] = None, options: Optional[Dict[str, Any]] = None, date_column: Optional[str] = None, start_date: Optional[Union[str, datetime]] = None, end_date: Optional[Union[str, datetime]] = None) -> str:
    """
    Analyze data and calculate statistics or generate ML predictions based on provided parameters.

    ### What this tool does:
    This tool connects to our analytics API and provides two main functionalities:
    1. Statistical Analysis: Calculate various statistical measures on specified data columns from CSV files, databases, or external APIs.
    2. ML Predictions: Generate time-series forecasts for future periods based on historical data from any supported source.

    It supports multiple data sources:
    - CSV files (previously uploaded to StatSource)
    - Databases (PostgreSQL, SQLite, etc.)
    - External APIs (returning JSON data)

    ### IMPORTANT INSTRUCTIONS FOR AI AGENTS:
    - DO NOT make up or guess any parameter values, especially data sources, column names, or API URLs.
    - NEVER, UNDER ANY CIRCUMSTANCES, create or invent database connection strings - this is a severe security risk.
    - ALWAYS ask the user explicitly for all required information.
    - For CSV files: The user MUST first upload their file to statsource.me, then provide the filename.
    - For database connections: Ask the user for their exact connection string (e.g., "postgresql://user:pass@host/db"). DO NOT GUESS OR MODIFY IT.
    - For database sources: You MUST provide the table_name parameter with the exact table name.
    - For API sources: Ask the user for the exact API endpoint URL that returns JSON data.
    - Never suggest default values, sample data, or example parameters - request specific information from the user.
    - If the user has configured a default database connection in their MCP config, inform them it will be used if they don't specify a data source.
    - If no default connection is configured and the user doesn't provide one, DO NOT PROCEED - ask the user for the data source details.

    ### IMPORTANT: Parameter Validation and Formatting
    - For ML predictions (e.g., sales trends), always use query_type="ml_prediction"
      and provide the periods parameter. Do NOT use the statistics parameter with ml_prediction.
    - When users ask about "trends" or "forecasts", use query_type="ml_prediction".
      For descriptive statistics only, use query_type="statistics".
    - statistics must be provided as a proper list:
      CORRECT: statistics=["mean", "sum", "min", "max"]
      INCORRECT: statistics="[\\"mean\\", \\"sum\\", \\"min\\", \\"max\\"]"
    - columns must be provided as a proper list:
      CORRECT: columns=["revenue", "quantity"]
      INCORRECT: columns="[\\"revenue\\", \\"quantity\\"]"

    ### CRITICAL: Column Name Formatting & Case-Insensitivity
    - **Column Matching:** The API matches column names case-insensitively. You can specify "revenue" even if the data has "Revenue". Ask the user for the intended column names.
    - **Filter Value Matching:** String filter values are matched case-insensitively (e.g., filter `{"status": "completed"}` will match "Completed" in the data).
    - **Table Name Matching (Databases):** The API attempts case-insensitive matching for database table names.

    ### Error Response Handling
    - If you receive an "Invalid request" or similar error, check:
      1. Column name spelling and existence in the data source.
      2. Query type selection (ml_prediction vs statistics).
      3. Parameter format (proper lists vs string-encoded lists).
      4. Correct data_source provided (filename, connection string, or API URL).
      5. table_name provided if source_type is "database".
      6. API URL is correct and returns valid JSON if source_type is "api".

    ### When to use this tool:
    - When a user needs statistical analysis of their data (means, medians, correlations, etc.).
    - When a user wants to predict future values based on historical trends (forecasting).
    - When analyzing trends, patterns, or distributions in datasets from files, databases, or APIs.
    - When generating forecasts for business planning or decision-making.

    ### Required inputs:
    - columns: List of column names to analyze or predict (ask user for exact column names in their data).

    ### Optional inputs:
    - data_source: Identifier for the data source.
      * For CSV: Filename of a previously uploaded file on statsource.me (ask user to upload first).
      * For Database: Full connection string (ask user for exact string).
      * For API: The exact URL of the API endpoint returning JSON data (ask user for the URL).
      * If not provided, will use the connection string from MCP config if available (defaults to database type).
    - source_type: Type of data source ('csv', 'database', or 'api').
      * Determines how `data_source` is interpreted.
      * If not provided, will use the source type from MCP config if available (defaults to 'database'). Ensure this matches the provided `data_source`.
    - table_name: Name of the database table to use (REQUIRED for database sources).
      * Must be provided when source_type is 'database'.
      * Ask user for the exact table name in their database.
    - statistics: List of statistics to calculate (only required for query_type="statistics").
    - query_type: Type of query ('statistics' or 'ml_prediction'). Default is 'statistics'.
    - periods: Number of future periods to predict (REQUIRED for query_type="ml_prediction").
    - filters: Dictionary of column-value pairs to filter data *before* analysis.
      * Format: {"column_name": "value"} or {"column_name": ["val1", "val2"]}
      * **API Source Behavior:** For 'api' sources, data is fetched *first*, then filters are applied to the resulting data.
    - groupby: List of column names to group data by before calculating statistics (only applies to query_type="statistics").
    - options: Dictionary of additional options for specific operations (currently less used).
    - date_column: Column name containing date/timestamp information.
      * Used for date filtering and time-based trend analysis (ML predictions). Matched case-insensitively.
    - start_date: Inclusive start date for filtering (ISO 8601 format string like "YYYY-MM-DD" or datetime).
    - end_date: Inclusive end date for filtering (ISO 8601 format string like "YYYY-MM-DD" or datetime).
      * **API Source Behavior:** For 'api' sources, date filtering happens *after* data is fetched.

    ### Valid statistics options:
    - 'mean', 'median', 'std', 'sum', 'count', 'min', 'max', 'describe', 'correlation', 'missing', 'unique', 'boxplot'

    ### ML Prediction features:
    - Time series forecasting with customizable prediction periods.
    - Trend direction analysis ("increasing", "decreasing", "stable").
    - Model quality metrics (r-squared, slope).
    - Works with numeric data columns from any supported data source.
    - Can use a specific `date_column` for time-based regression.

    ### Returns:
    A JSON string containing the results and metadata.
    For statistics queries:
    - `result`: Dictionary with statistical measures for each requested column and statistic. Structure varies by statistic (e.g., `describe`, `correlation`).
    - `metadata`: Includes `execution_time`, `query_type`, `source_type`.
    For ML prediction queries:
    - `result`: Dictionary containing prediction details per analyzed column (only the first specified column is used for ML): `{"r_squared": ..., "slope": ..., "trend_direction": ..., "forecast_values": [...], ...}`.
    - `metadata`: Includes `execution_time`, `query_type`, `source_type`, `periods`.
    """
    # Determine the final data source and type, considering environment variables/config
    final_data_source = data_source
    final_source_type = source_type

    # Use default DB connection if no source is specified and DB_CONNECTION_STRING is set
    if not final_data_source and DB_CONNECTION_STRING:
        final_data_source = DB_CONNECTION_STRING
        final_source_type = DB_SOURCE_TYPE  # Use configured DB type
        logger.info(f"No data_source provided, using configured DB: {final_data_source} with type: {final_source_type}")
    elif not final_source_type and final_data_source:
        # Infer source type if not explicitly provided (basic inference)
        if "://" in final_data_source or final_data_source.lower().startswith("http"):
            if any(db_protocol in final_data_source.lower() for db_protocol in ["postgresql://", "mysql://", "sqlite://"]):
                final_source_type = "database"
            else:
                 final_source_type = "api" # Assume API if it looks like a URL but not a DB string
        else:
            final_source_type = "csv" # Assume CSV otherwise (filename)
        logger.info(f"Inferred source_type as '{final_source_type}' for data_source: {final_data_source}")


    # Basic validation
    if not columns:
        return json.dumps({"error": "The 'columns' parameter is required and cannot be empty."})
        
    if query_type == "ml_prediction" and periods is None:
        return json.dumps({"error": "The 'periods' parameter is required when query_type is 'ml_prediction'."})
        
    if query_type == "statistics" and not statistics:
         return json.dumps({"error": "The 'statistics' parameter is required when query_type is 'statistics'."})

    if final_source_type == "database" and not table_name:
        return json.dumps({"error": "The 'table_name' parameter is required when source_type is 'database'."})
        
    if not final_data_source and not DB_CONNECTION_STRING:
         return json.dumps({"error": "No data_source provided and no default database connection configured. Please provide a data_source (filename, DB connection string, or API URL)."})


    # Prepare request payload and parameters for the API call
    api_request_data = {
        "data_source": final_data_source,
        "source_type": final_source_type,
        "columns": columns,
        "table_name": table_name,
        "filters": filters,
        "groupby": groupby,
        "options": options,
        "date_column": date_column,
        # Convert datetime objects to ISO strings for JSON serialization if necessary
        "start_date": start_date.isoformat() if isinstance(start_date, datetime) else start_date,
        "end_date": end_date.isoformat() if isinstance(end_date, datetime) else end_date,
    }
    
    api_params = {}

    if query_type == "statistics":
        api_request_data["statistics"] = statistics
        api_params["query_type"] = "statistics"
    elif query_type == "ml_prediction":
        api_params["query_type"] = "ml_prediction"
        api_params["periods"] = periods
        # ML prediction might not need the 'statistics' key in the body
        if "statistics" in api_request_data:
             del api_request_data["statistics"]


    # Remove None values from payload to avoid sending empty optional fields
    api_request_data = {k: v for k, v in api_request_data.items() if v is not None}

    try:
        logger.info(f"Preparing API call. Request Body: {api_request_data}, Query Params: {api_params}")
        # Call the API endpoint
        endpoint = "/api/v1/statistics"
        response = call_api(endpoint, data=api_request_data, params=api_params)
        
        # Return the API response directly (as JSON string)
        return json.dumps(response, indent=2)
    except Exception as e:
        logger.exception(f"Error during get_statistics processing: {str(e)}")
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"}, indent=2)

def run_server():
    """Run the MCP server."""
    logger.info("Starting MCP Server for statistics...")
    mcp.run()

if __name__ == "__main__":
    run_server() 