# Installation

## Python Package

Install via pip:

```bash
pip install signature-recovery
```

## Windows

Download the latest MSI from the releases page and double-click the installer. A desktop shortcut named **Signature Recovery** will appear.

## macOS

Download the DMG, open it, and drag the **Signature Recovery.app** into your Applications folder.

## Docker

Run the container with a mounted volume:

```bash
docker run -v /path/to/pst:/data your/image recover-signatures extract /data/file.pst
```
