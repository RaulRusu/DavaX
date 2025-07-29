from setuptools import setup, find_packages

setup(
    name="shared_core",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "oracledb",
        "pydantic",
        'pydantic-settings'
    ],
)