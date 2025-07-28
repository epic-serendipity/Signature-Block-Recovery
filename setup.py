from pathlib import Path
from setuptools import setup, find_packages

README = Path(__file__).with_name("README.md").read_text()

setup(
    name="signature_recovery",
    version="0.1.0",
    description="Recover signature blocks from data files",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["template"],
    install_requires=[
        "flask>=2.0.0",       # for signature_recovery.api
        "openpyxl>=3.0.0",    # for signature_recovery.exporter Excel support
        "pandas>=1.0.0",      # if used for JSON/CSV conversions in exporter
        "pyyaml>=5.4",        # YAML-based configuration
        "pyvirtualdisplay>=3.0",  # headless GUI tests
        "argcomplete>=3.0",   # shell completion support
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "recover-signatures=signature_recovery.cli.main:main",
        ],
    },
)
