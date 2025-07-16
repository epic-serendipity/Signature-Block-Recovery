from setuptools import setup, find_packages

setup(
    name="signature_recovery",
    version="0.1.0",
    packages=find_packages(),
    py_modules=["template"],
    install_requires=[
        "flask>=2.0.0",       # for signature_recovery.api
        "openpyxl>=3.0.0",    # for signature_recovery.exporter Excel support
        "pandas>=1.0.0",      # if used for JSON/CSV conversions in exporter
        "pyyaml>=5.4",        # YAML-based configuration
        "pyvirtualdisplay>=3.0",  # headless GUI tests
    ],
    entry_points={
        "console_scripts": [
            "recover-signatures=signature_recovery.cli.main:main",
        ],
    },
)
