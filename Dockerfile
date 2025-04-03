# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
# Copy setup.py and MANIFEST.in for installation
COPY setup.py MANIFEST.in ./
COPY README.md ./
# Copy the main package directory
COPY mcp_server_stats ./mcp_server_stats

# Install the project itself
RUN pip install --no-cache-dir .

# Make port 80 available to the world outside this container (if your server listens on a port - adjust if needed)
# EXPOSE 80 # MCP usually communicates over stdin/stdout, so this might not be necessary

# Define environment variables (optional, can be overridden at runtime)
# ENV API_KEY="your_default_api_key"
# ENV DB_CONNECTION_STRING="your_default_db_string"
# ENV DB_SOURCE_TYPE="database"

# Run the application when the container launches
CMD ["python", "-m", "mcp_server_stats"] 