from setuptools import setup, find_packages

setup(
    name="conjoint-mcp-server",
    version="0.1.0",
    description="Choice Based Conjoint Design Generator MCP Server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "mcp>=1.1.0",
        "pydantic>=2.7.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.1",
        "numpy>=1.26.0",
        "scipy>=1.11.0",
        "pandas>=2.2.0",
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "conjoint-mcp=conjoint_mcp.server:main",
        ],
    },
)
