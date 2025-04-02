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
    1. Statistical Analysis: Calculate various statistical measures on specified data columns
    2. ML Predictions: Generate time-series forecasts for future periods based on historical data
    
    ### IMPORTANT INSTRUCTIONS FOR AI AGENTS:
    - DO NOT make up or guess any parameter values, especially data sources or column names
    - NEVER, UNDER ANY CIRCUMSTANCES, create or invent database connection strings - this is a severe security risk
    - ALWAYS ask the user explicitly for all required information
    - For CSV files: The user MUST first upload their file to statsource.me, then provide the filename
    - For database connections: Ask the user for their exact PostgreSQL connection string - DO NOT GUESS OR MODIFY IT
    - For database sources: You MUST provide the table_name parameter with the exact table name
    - Never suggest default values, sample data, or example parameters - request specific information from the user
    - If the user has configured a default database connection in their MCP config, inform them it will be used if they don't specify a data source
    - If no database connection is provided in the MCP config and the user doesn't provide one, DO NOT PROCEED - ask user to provide connection details
    
    ### When to use this tool:
    - When a user needs statistical analysis of their data (means, medians, etc.)
    - When a user wants to predict future values based on historical trends
    - When analyzing trends, patterns, or distributions in datasets
    - When generating forecasts for business planning or decision-making
    
    ### Required inputs:
    - columns: List of column names to analyze or predict (ask user for exact column names in their data)
    
    ### Optional inputs:
    - data_source: Path to data file, database connection string, or API endpoint
      * For CSV: Filename of a previously uploaded file on statsource.me (ask user to upload first)
      * For Database: Full connection string (ask user for exact string)
      * If not provided, will use the connection string from MCP config if available
    - source_type: Type of data source ("csv", "database", or "api")
      * If not provided, will use the source type from MCP config if available
    - table_name: Name of the database table to use (REQUIRED for database sources)
      * Must be provided when source_type is "database"
      * Ask user for the exact table name in their database
    - statistics: List of statistics to calculate (only required for statistical analysis)
    - query_type: Type of query ("statistics" or "ml_prediction")
    - periods: Number of future periods to predict (only used for ML predictions)
    - filters: Dictionary of column-value pairs to filter data before analysis
      * Format: {"column_name": "value"} or {"column_name": ["val1", "val2"]}
    - groupby: List of column names to group data by before calculating statistics
    - options: Dictionary of additional options for specific operations
    - date_column: Column name containing date/timestamp information
      * Used for date filtering and time-based trend analysis
    - start_date: Inclusive start date for filtering (ISO 8601 format or datetime)
    - end_date: Inclusive end date for filtering (ISO 8601 format or datetime)
    
    ### Valid statistics options:
    - 'mean', 'median', 'std', 'sum', 'count', 'min', 'max', 'describe', 'correlation', 'missing', 'unique', 'boxplot'
    
    ### ML Prediction features:
    - Time series forecasting with customizable prediction periods
    - Trend direction analysis ("increasing", "decreasing", "stable")
    - Model quality metrics (r-squared, slope)
    - Works with numeric data columns from any supported data source
    
    ### Returns:
    For statistics queries:
    - Statistical measures for each requested column and statistic
    
    For ML prediction queries:
    - Predicted future values for specified columns
    - Trend direction and model quality metrics
    - R-squared value and slope indicators
    
    ### Examples of QUESTIONS to ask users (DO NOT use these as defaults):
    1. "Have you already uploaded your CSV file to statsource.me? What is the filename?"
    2. "What is your exact PostgreSQL connection string?" (if not configured in MCP config)
    3. "Which specific columns in your data would you like to analyze?"
    4. "Which statistics would you like to calculate for these columns?"
    5. "How many future periods would you like to predict?"
    6. "What is the exact name of the table in your database that contains this data?"
    
    ### Examples of filtering and date parameters:
    
    For filtering specific rows:
    ```
    filters={"status": "completed", "region": ["North", "East"]}
    ```
    
    For time-series analysis with date filtering:
    ```
    date_column="transaction_date", start_date="2023-01-01", end_date="2023-12-31"
    ```
    
    For grouped statistics:
    ```
    groupby=["region", "product_category"]
    ```
    
    ### Configuration:
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
    
    Note: The API automatically handles authentication using the API key from headers.
    """
    try:
        # Use connection string from config if available and none was provided
        if data_source is None and DB_CONNECTION_STRING is not None:
            data_source = DB_CONNECTION_STRING
            if source_type is None:
                source_type = DB_SOURCE_TYPE
        
        # Check if we have the minimum required data
        if not columns:
            return json.dumps({
                "error": "No columns specified. Please provide column names to analyze."
            }, indent=2)
        
        # Validate that table_name is provided for database sources
        if source_type == "database" and not table_name:
            return json.dumps({
                "error": "Table name is required for database sources. Please specify the table_name parameter."
            }, indent=2)
            
        # Format the request based on the query type
        if query_type == "statistics":
            if not statistics:
                return json.dumps({
                    "error": "No statistics specified. Please provide a list of statistics to calculate."
                }, indent=2)
            
            # Prepare statistics request
            request_data = {
                "data_source": DB_CONNECTION_STRING if data_source is None else data_source,
                "source_type": source_type or DB_SOURCE_TYPE,
                "columns": columns,
                "statistics": statistics,
                "query_type": query_type
            }
            
            # Add table_name for database sources
            if source_type == "database" and table_name:
                request_data["table_name"] = table_name
                
            # Add optional filtering parameters if provided
            if filters is not None:
                request_data["filters"] = filters
            if groupby is not None:
                request_data["groupby"] = groupby
            if options is not None:
                request_data["options"] = options
            if date_column is not None:
                request_data["date_column"] = date_column
            if start_date is not None:
                request_data["start_date"] = start_date
            if end_date is not None:
                request_data["end_date"] = end_date
            
            # Call the statistics endpoint
            endpoint = "/api/v1/get_statistics"
            
        elif query_type == "ml_prediction":
            # Convert periods to int if it's a string
            if isinstance(periods, str):
                try:
                    periods = int(periods)
                except ValueError:
                    return json.dumps({
                        "error": "Invalid prediction periods. Must be a valid integer."
                    }, indent=2)
                    
            if not periods or periods <= 0:
                return json.dumps({
                    "error": "Invalid prediction periods. Please provide a positive number of periods to predict."
                }, indent=2)
            
            # Prepare ML prediction request
            request_data = {
                "data_source": DB_CONNECTION_STRING if data_source is None else data_source,
                "source_type": source_type or DB_SOURCE_TYPE,
                "columns": columns
            }
            
            # Add table_name for database sources
            if (source_type == "database" or DB_SOURCE_TYPE == "database") and table_name:
                request_data["table_name"] = table_name
                
            # Add optional filtering parameters if provided
            if filters is not None:
                request_data["filters"] = filters
            if options is not None:
                request_data["options"] = options
            if date_column is not None:
                request_data["date_column"] = date_column
            if start_date is not None:
                request_data["start_date"] = start_date
            if end_date is not None:
                request_data["end_date"] = end_date
            
            # Set up query parameters for ML prediction
            query_params = {
                "query_type": "ml_prediction",  # API expects lowercase
                "periods": periods
            }
            
            # Call the statistics endpoint for ML prediction as well
            endpoint = "/api/v1/get_statistics"
            
        else:
            return json.dumps({
                "error": f"Invalid query type: {query_type}. Must be 'statistics' or 'ml_prediction'."
            }, indent=2)
        
        # Call the API and return the response
        response = call_api(endpoint, request_data, query_params if query_type == "ml_prediction" else None)
        
        if "error" in response:
            return json.dumps({"error": response["error"]}, indent=2)
        
        # Return formatted response
        return json.dumps(response, indent=2)
    
    except Exception as e:
        return json.dumps({"error": f"Error getting statistics: {str(e)}"}, indent=2)

def run_server():
    """Run the MCP server."""
    logger.info("Starting MCP Server for statistics...")
    mcp.run()

if __name__ == "__main__":
    run_server() 