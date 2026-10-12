# MP1 Data Pipeline

The MP1 pipeline loads CSV data and YAML settings from command-line paths, then validates and cleans the data before saving a CSV result. `src/data_loaders.py` selects a loader for CSV, JSON, or YAML files. `src/data_validator.py` checks required columns and removes rows with invalid values in configured numeric columns. `src/data_processor.py` applies duplicate removal, missing-value handling, and outlier filtering in that order. `src/data_output.py` creates the output directory and saves the cleaned DataFrame, while `src/utils.py` configures logging and validates input paths. `config/config.yaml` keeps dataset-specific columns and cleaning choices outside the Python modules. The example below processes the included sample data and writes the cleaned CSV under `output/`.

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
