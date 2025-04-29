#!/usr/bin/env python3
"""
This script provides a mock example that simulates the GCS analysis output
based on the given EA-Cost-Actual.csv example, without requiring actual GCP credentials.
"""

import argparse
from datetime import datetime, timedelta
import random
import pandas as pd

def format_size(size_bytes):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def generate_mock_files(bucket_name, folder, file_count=10, date_str="04-29-2025"):
    """Generate mock file data for demonstration"""
    date_obj = datetime.strptime(date_str, "%m-%d-%Y")
    formatted_date = date_obj.strftime("%b %d, %Y")
    
    # Sample file types and extensions
    file_types = [
        ("EA-Cost-Actual.csv", "text/csv", 141.3 * 1024 * 1024),  # 141.3 MB
        ("billing-report", "text/csv", random.uniform(50, 200) * 1024 * 1024),
        ("usage-stats", "application/json", random.uniform(10, 50) * 1024 * 1024),
        ("resource-inventory", "text/csv", random.uniform(20, 100) * 1024 * 1024),
        ("monthly-summary", "application/pdf", random.uniform(5, 15) * 1024 * 1024),
        ("cloud-spend", "text/csv", random.uniform(80, 150) * 1024 * 1024),
        ("cost-allocation", "text/csv", random.uniform(60, 120) * 1024 * 1024),
        ("project-metrics", "application/json", random.uniform(30, 70) * 1024 * 1024),
        ("optimization-report", "application/pdf", random.uniform(8, 25) * 1024 * 1024),
        ("forecast-data", "text/csv", random.uniform(40, 90) * 1024 * 1024)
    ]

    # Ensure we have enough types for requested count
    while len(file_types) < file_count:
        file_types.append(("generic-data", "text/plain", random.uniform(10, 100) * 1024 * 1024))
    
    files = []
    total_size = 0
    
    for i in range(min(file_count, len(file_types))):
        base_name, content_type, size = file_types[i]
        # Add some randomization to filenames
        if i > 0:  # Keep the first file exactly as EA-Cost-Actual.csv
            if "." in base_name:
                name_part, ext = base_name.rsplit(".", 1)
                file_name = f"{name_part}-{i}.{ext}"
            else:
                file_name = f"{base_name}-{i}"
        else:
            file_name = base_name

        if folder:
            full_path = f"{folder}/{file_name}"
        else:
            full_path = file_name
            
        # Generate a random time on the specified date
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        timestamp = date_obj.replace(hour=hour, minute=minute, second=second)
        formatted_time = timestamp.strftime("%I:%M:%S %p")
        
        files.append({
            "Name": full_path,
            "Size": format_size(size),
            "Size_Bytes": size,
            "Type": content_type,
            "Created": f"{formatted_date}, {formatted_time}",
            "Storage_Class": "Standard",
            "Last_Modified": f"{formatted_date}, {formatted_time}",
            "Public_Access": "Not public",
            "Generation": f"{random.randint(1600000000000000, 1700000000000000)}",
            "Encryption": "Google-managed"
        })
        total_size += size
    
    return files, total_size

def mock_gcs_analysis(bucket_name, folder=None, limit=10, date="04-29-2025", export=False, verbose=False):
    """Mock GCS bucket analysis to demonstrate output format"""
    print(f"\nMOCK ANALYSIS (No GCP credentials required)")
    print(f"Analyzing bucket: {bucket_name}")
    if folder:
        print(f"Folder: {folder}")
    print(f"Date filter: {date}")
    
    # Generate more files than the limit to show total count vs. analyzed count
    total_file_count = 25  # Simulate total files for the date
    print(f"Counting total files for the specified date...")
    print(f"Total files for {date}: {total_file_count}")
    
    print(f"Limiting analysis to {limit} files")
    
    files, total_size = generate_mock_files(bucket_name, folder, limit, date)
    
    if verbose:
        print("\nFile Analysis:")
        print(f"{'Name':<50} {'Size':<15} {'Type':<20} {'Created':<30} {'Storage Class':<15} {'Last Modified':<30}")
        print("-" * 160)
        
        for file in files:
            print(f"{file['Name']:<50} {file['Size']:<15} {file['Type']:<20} "
                f"{file['Created']:<30} {file['Storage_Class']:<15} {file['Last_Modified']:<30}")
    
    print("\nSummary:")
    print(f"Total files analyzed: {len(files)} (of {total_file_count} total for this date)")
    print(f"Total size: {format_size(total_size)}")
    
    if export:
        df = pd.DataFrame(files)
        output_file = f"mock_gcs_analysis_{bucket_name.replace('/','-')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        print(f"\nResults exported to {output_file}")
    
    return files

def main():
    parser = argparse.ArgumentParser(description="Mock GCS Bucket Analysis (No credentials required)")
    parser.add_argument("bucket_name", help="Name of the GCS bucket to analyze")
    parser.add_argument("--folder", help="Folder/prefix within the bucket")
    parser.add_argument("--limit", type=int, default=10, help="Limit the number of files to analyze")
    parser.add_argument("--date", default="04-29-2025", help="Filter by date (format: MM-DD-YYYY)")
    parser.add_argument("--export", action="store_true", help="Export results to CSV")
    parser.add_argument("--verbose", action="store_true", help="Show detailed file listing")
    
    args = parser.parse_args()
    
    # Remove gs:// prefix if present
    bucket_name = args.bucket_name
    if bucket_name.startswith("gs://"):
        bucket_name = bucket_name[5:]
    
    mock_gcs_analysis(bucket_name, args.folder, args.limit, args.date, args.export, args.verbose)

if __name__ == "__main__":
    main()