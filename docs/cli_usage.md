# Command Line Usage

## Extract

```bash
recover-signatures extract --input mail.pst --index sigs.db --threads 4 --batch-size 500
```

Builds a searchable database from your PST file. Optional flags control performance and filtering.

## Query

```bash
recover-signatures query --index sigs.db --q "John Doe" --page 1 --size 10
```

Search the index for matching signatures.

## Export

```bash
recover-signatures export --index sigs.db --format csv --out sigs.csv
```

Exports all signatures to your chosen format (`csv`, `json`, or `xlsx`).

## Metrics

```bash
recover-signatures metrics --index sigs.db
```

Dump runtime statistics and index details.

## Global Options

* `--threads N` – number of worker threads
* `--batch-size N` – messages per batch
* `--min-confidence FLOAT` – filter results
* `--verbose` – enable debug logging
* `--version` – show program version
