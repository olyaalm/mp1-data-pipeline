# MP1 Data Pipeline

The MP1 pipeline loads CSV data and YAML settings from command-line paths, then validates and cleans the data before saving a CSV result. `src/data_loaders.py` selects a loader for CSV, JSON, or YAML files. `src/data_validator.py` checks required columns and removes rows with invalid values in configured numeric columns. `src/data_processor.py` applies duplicate removal, missing-value handling, and outlier filtering in that order. `src/data_output.py` creates the output directory and saves the cleaned DataFrame, while `src/utils.py` configures logging and validates input paths. `config/config.yaml` keeps dataset-specific columns and cleaning choices outside the Python modules. The example below processes the included sample data and writes the cleaned CSV under `output/`.

## Run the Pipeline

```powershell
python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
```

## Example Output

```text
Cleaning report:
{'rows_before': 3, 'rows_after': 3, 'rows_removed': 0, 'columns_before': 3, 'columns_after': 3, 'columns_removed': 0}
```
