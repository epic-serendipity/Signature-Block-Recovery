# Signature Block Recovery

Recover email signature blocks from PST files.

To enable direct PST parsing via `pypff`, install with `pip install signature-recovery[pst]`.

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
   pip install signature-recovery        # GUI & core features
   pip install signature-recovery[pst]   # add PST parsing support via pypff
   recover-signatures extract --input my.pst --index sigs.db
   ```
