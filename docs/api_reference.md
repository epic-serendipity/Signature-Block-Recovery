# API Reference

All endpoints are prefixed with `/api`.

## `GET /api/search`

Query parameters:

* `q` – search string
* `company` – optional company filter
* `title` – optional title filter
* `page` – page number
* `size` – results per page

Example response:

```json
{
  "results": [
    {"name": "John Doe", "email": "john@example.com", "confidence": 0.98}
  ],
  "total": 1,
  "page": 1,
  "size": 10
}
```

Example request using `curl`:

```bash
curl "http://localhost:5000/api/search?q=john&page=1&size=10"
```
