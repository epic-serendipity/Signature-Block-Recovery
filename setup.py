from pathlib import Path
from setuptools import setup, find_packages

# Explicitly read README with UTF-8 to avoid encoding issues on Windows
README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="signature_recovery",
    version="0.1.0",
    description="Recover signature blocks from data files",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    py_modules=["template"],
    install_requires=[
        "pypff>=0.6.0",  # PST parsing library
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "recover-gui=signature_recovery.gui.app:main",
            "recover-signatures=signature_recovery.cli.main:main",
        ]
    },
)
