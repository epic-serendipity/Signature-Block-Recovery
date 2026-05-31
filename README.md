# Signature Block Recovery

Recover email signature blocks from PST files.

### Pre-install PST support

Before you install this package, you **must** install `pypff`.

**Via Conda (strongly recommended)**
```bash
conda install -c conda-forge pypff
```

**Or build from source**
```bash
git clone https://github.com/libyal/libpff.git
cd libpff
./synclibs.sh
./autogen.sh && ./configure && make && sudo make install
cd bindings/python
pip install .
```

### Installation
```bash
pip install signature-recovery
# or for local dev:
pip install -e .
```

## Quick Start

1. **Download the Installer**  
   Grab the latest release from the [Releases](https://github.com/epic-serendipity/Signature-Block-Recovery/releases) page.

2. **Launch the GUI**  
   Run the installer and start the app with a single click or from a terminal:
   ```bash
   recover-gui
   ```

3. **Command Line**
   Advanced users can work directly with the CLI:
   ```bash
   recover-signatures extract --input my.pst --index sigs.db
   ```
