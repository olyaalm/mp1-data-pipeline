# MP1 Data Pipeline

This command-line pipeline reads a data file and a YAML config, then saves a cleaned CSV. The loader module supports CSV, JSON, and YAML files. The validator checks required columns and converts configured numeric fields, while dropping rows that contain invalid numeric text. The processor removes duplicate rows, handles missing values, and then removes outliers. The output module creates the destination folder and saves the CSV without an index. Shared logging and file checks are in `src/utils.py`, and dataset-specific settings are in `config/config.yaml`. The example uses the course sample data and shows the resulting cleaning report.

## Run the Pipeline

```powershell
python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
```

## Example Output

```text
10:15:02 INFO     src.utils — Input file validated: fixtures/sample_data.csv
10:15:02 INFO     src.utils — Input file validated: config/config.yaml
10:15:02 INFO     src.data_loaders — Loaded CSV file: fixtures/sample_data.csv (100 rows)
10:15:02 INFO     src.data_loaders — Loaded YAML file: config/config.yaml
10:15:02 WARNING  src.data_validator — Removed 2 rows with invalid numeric values in rating
10:15:02 DEBUG    src.data_validator — Validation: 100 -> 98 rows (2 removed)
10:15:02 INFO     __main__ — Validation complete: 100 -> 98 rows
10:15:02 DEBUG    src.data_processor — remove_duplicates: 98 -> 96 rows
10:15:02 DEBUG    src.data_processor — handle_missing (rows): removed 2
10:15:02 DEBUG    src.data_processor — rating (iqr, threshold=1.5): lower=43.625, upper=106.625, removed=2
10:15:02 DEBUG    src.data_processor — remove_outliers (iqr, threshold=1.5): removed 2 rows
10:15:02 INFO     __main__ — Processing complete: 98 -> 92 rows
10:15:02 DEBUG    src.data_output — Saved 92 rows to output/clean.csv
10:15:02 INFO     __main__ — Saved cleaned data to output/clean.csv

Cleaning report:
{'rows_before': 98, 'rows_after': 92, 'rows_removed': 6, 'columns_before': 5, 'columns_after': 5, 'columns_removed': 0}
```
