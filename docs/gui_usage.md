# GUI Usage

Launch the interface:

```bash
recover-signatures gui --index sigs.db
```

The window contains several panels:

* **Search** – enter names, emails, or keywords and click **Search**.
* **Filters** – choose date range, company, and title. Adjust the **confidence** slider to hide low-probability results.
* **Results** – matching signatures appear in a table. Click column headers to sort.
* **Pagination** – navigate between pages and change page size.
* **Alerts** – warnings and errors are displayed here.

Filters are seeded from the existing index on startup so you can immediately narrow results.
