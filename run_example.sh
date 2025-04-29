#!/bin/bash

# Example script to run the GCS analysis tool on the specified bucket and date

# Ensure credentials are set
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo "WARNING: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"
    echo "Please set it with: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json"
    
    echo -e "\nRunning in mock mode instead (no credentials required)..."
    python mock_example.py test-gcs-2025423 --folder dataset-examples --limit 10 --date 04-29-2025
    exit 0
fi

# Run the analyzer with the given parameters (non-verbose mode - no file listing)
echo -e "\nRunning GCS analysis (summary only):"
python gcs_analysis.py test-gcs-2025423 --folder dataset-examples --limit 10 --date 04-29-2025

echo ""
echo "Want to see the file listing? Add the --verbose flag:"
echo "python gcs_analysis.py test-gcs-2025423 --folder dataset-examples --limit 10 --date 04-29-2025 --verbose"

echo ""
echo "To view the specific file EA-Cost-Actual.csv from April 29, 2025:"
echo "python gcs_analysis.py test-gcs-2025423 --folder dataset-examples --prefix EA-Cost-Actual.csv --date 04-29-2025"