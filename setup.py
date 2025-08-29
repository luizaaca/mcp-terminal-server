from setuptools import setup, find_packages

setup(
    name="mcp-terminal-server",
    version="0.1.0-beta",
    description="MCP Terminal Server",
    py_modules=["cli"],  
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        'console_scripts': [
            'mcp-terminal-server=cli:main',
        ],
    },
    python_requires=">=3.8",
)