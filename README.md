# GCS Bucket Analysis Tool

A Python tool for analyzing Google Cloud Storage (GCS) buckets, calculating file sizes, and filtering by date.

## Features

- List files in a GCS bucket with filtering options
- Calculate total size of files
- Filter files by date
- Limit the number of files to analyze
- Export results to CSV

## Installation

1. Clone this repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Ensure you have Google Cloud credentials set up:
```
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

## Usage

```bash
python gcs_analysis.py BUCKET_NAME [--folder FOLDER] [--limit N] [--prefix PREFIX] [--date MM-DD-YYYY] [--export] [--verbose]
```

### Arguments:

- `BUCKET_NAME`: Name of the GCS bucket to analyze (required)
- `--folder FOLDER`: Folder/prefix path within the bucket
- `--limit N`: Limit analysis to N files
- `--prefix PREFIX`: Filter objects by prefix
- `--date MM-DD-YYYY`: Filter by date in MM-DD-YYYY format
- `--export`: Export results to CSV
- `--verbose`: Show detailed file listing (otherwise only shows summary)

### Example:

```bash
# Get total file count and size for 10 files in bucket "test-gcs-2025423" under folder "dataset-examples" from April 29, 2025
python gcs_analysis.py test-gcs-2025423 --folder dataset-examples --limit 10 --date 04-29-2025

# Show detailed file listing with verbose mode
python gcs_analysis.py test-gcs-2025423 --folder dataset-examples --limit 10 --date 04-29-2025 --verbose

# You can also use gs:// format
python gcs_analysis.py gs://test-gcs-2025423 --folder dataset-examples --limit 10 --date 04-29-2025
```

### No GCP Credentials?

Use the mock example script instead:

```bash
python mock_example.py test-gcs-2025423 --folder dataset-examples --limit 10 --date 04-29-2025
```

## Output

The tool displays:
- File name
- Size (human-readable)
- Content type
- Creation date
- Storage class
- Last modified date
- Public access status

It also provides a summary with total file count and total size.