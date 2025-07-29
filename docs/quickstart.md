# Quick Start

1. **Install**
   ```bash
   pip install signature-recovery
   ```
2. **Extract signatures**
   ```bash
   recover-signatures extract --input my.pst --index sigs.db
   ```
3. **Open the GUI**
   ```bash
   recover-signatures gui --index sigs.db
   ```
   This launches a window with search, filters, and results panels.
4. **Search, filter, export**
   Use the search box to find names or emails. Adjust filters and the confidence slider, then export results to CSV.

```text
┌─ GUI ───────────────────────────────────┐
│ Search [________] [Search]              │
│ Filters | Results | Pagination | Alerts │
└────────────────────────────────────────┘
```
