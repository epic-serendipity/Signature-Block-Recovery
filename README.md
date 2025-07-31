# Signature Block Recovery

Recover email signature blocks from PST files.

### Installation

- **Core & GUI only** (no PST parsing):
  ```bash
  pip install signature-recovery
  ```

- **With PST parsing support** (requires a locally built `pypff`):
  ```bash
  pip install signature-recovery[pst]
  ```

#### PST Parsing Support (Optional)

If you need to extract directly from Outlook PST files, you’ll need `pypff`, which isn’t available on PyPI.  

1. **Via Conda** (recommended):
   ```bash
   conda install -c conda-forge pypff
   ```

2. **Build from source**:

   * Clone the libpff repo: `git clone https://github.com/libyal/libpff.git`
   * Follow its build instructions to install `pypff` into your Python.
3. **Then install our extras**:

   ```bash
   pip install signature-recovery[pst]
   ```

Without `pypff`, you can still use all GUI and CLI features on existing indexes—you just won’t be able to run `extract --input file.pst` until it’s installed.

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
