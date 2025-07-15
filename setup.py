from setuptools import setup, find_packages

setup(
    name="signature_recovery",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "recover-signatures=signature_recovery.cli.main:main",
        ],
    },
)
