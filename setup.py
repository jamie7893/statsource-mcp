from setuptools import setup, find_packages
import os
from mcp_server_stats import __version__

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mcp-server-stats",
    version=__version__,
    author="Statsource Team",
    author_email="info@statsource.me",
    description="A Model Context Protocol server for statistical analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamie7893/statsource-mcp",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=0.1.0,<1.0.0",
        "requests>=2.31.0,<3.0.0",
        "pydantic>=2.4.2,<3.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
        "python-json-logger>=2.0.7,<3.0.0"
    ],
    entry_points={
        "console_scripts": [
            "mcp-server-stats=mcp_server_stats.server:run_server",
        ],
    },
) 