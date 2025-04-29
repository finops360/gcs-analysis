#!/usr/bin/env python3

import argparse
from google.cloud import storage
from datetime import datetime
import pandas as pd
import pytz

def list_bucket_objects(bucket_name, limit=None, prefix=None, date_filter=None):
    """
    List objects in a GCS bucket with optional filtering
    
    Args:
        bucket_name (str): Name of the GCS bucket
        limit (int, optional): Maximum number of files to return
        prefix (str, optional): Filter objects by prefix
        date_filter (str, optional): Filter by date in format MM-DD-YYYY
    
    Returns:
        list: List of storage blob objects
    """
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    
    filtered_blobs = []
    
    # Parse date filter if provided
    filter_date = None
    if date_filter:
        filter_date = datetime.strptime(date_filter, "%m-%d-%Y").date()
    
    for blob in blobs:
        # Apply date filter if provided
        if filter_date:
            # Convert the blob's updated time to the same timezone as filter_date
            blob_date = blob.updated.astimezone(pytz.UTC).date()
            if blob_date.strftime("%m-%d-%Y") != filter_date.strftime("%m-%d-%Y"):
                continue
        
        filtered_blobs.append(blob)
        
        # Apply limit if provided
        if limit and len(filtered_blobs) >= limit:
            break
    
    return filtered_blobs

def format_size(size_bytes):
    """
    Format bytes to human-readable format
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_content_type(blob):
    """
    Get content type of the blob
    """
    return blob.content_type if blob.content_type else "Unknown"

def count_all_files_by_date(bucket_name, prefix=None, date_filter=None):
    """
    Count all files in a bucket for a specific date without applying a limit
    
    Args:
        bucket_name (str): Name of the GCS bucket
        prefix (str, optional): Filter objects by prefix
        date_filter (str, optional): Filter by date in format MM-DD-YYYY
    
    Returns:
        int: Total number of files for the given date
    """
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    
    file_count = 0
    
    # Parse date filter if provided
    filter_date = None
    if date_filter:
        filter_date = datetime.strptime(date_filter, "%m-%d-%Y").date()
    
    for blob in blobs:
        # Apply date filter if provided
        if filter_date:
            # Convert the blob's updated time to the same timezone as filter_date
            blob_date = blob.updated.astimezone(pytz.UTC).date()
            if blob_date.strftime("%m-%d-%Y") != filter_date.strftime("%m-%d-%Y"):
                continue
        
        file_count += 1
    
    return file_count

def analyze_gcs_bucket(bucket_name, limit=None, prefix=None, date_filter=None, export_csv=False, verbose=False):
    """
    Analyze GCS bucket objects and display summary information
    
    Args:
        bucket_name (str): Name of the GCS bucket
        limit (int, optional): Maximum number of files to analyze
        prefix (str, optional): Filter objects by prefix
        date_filter (str, optional): Filter by date in format MM-DD-YYYY
        export_csv (bool, optional): Export results to CSV
        verbose (bool, optional): Whether to list all files or just show summary
    """
    print(f"Analyzing bucket: {bucket_name}")
    if prefix:
        print(f"Prefix filter: {prefix}")
    if date_filter:
        print(f"Date filter: {date_filter}")
    
    try:
        # First count total number of files for the date (without limit)
        print("Counting total files for the specified date...")
        total_file_count = count_all_files_by_date(bucket_name, prefix, date_filter)
        print(f"Total files for {date_filter}: {total_file_count}")
        
        if limit:
            print(f"Limiting analysis to {limit} files")
        else:
            # If no limit specified, use total count
            limit = total_file_count
        
        # Now get the limited list
        blobs = list_bucket_objects(bucket_name, limit, prefix, date_filter)
        
        if not blobs:
            print("No objects found matching the criteria.")
            return
        
        total_size = 0
        results = []
        
        # Only show detailed listing if verbose mode is enabled
        if verbose:
            print("\nFile Analysis:")
            print(f"{'Name':<50} {'Size':<15} {'Type':<20} {'Created':<25} {'Storage Class':<15} {'Last Modified':<25}")
            print("-" * 150)
        
        for blob in blobs:
            total_size += blob.size
            created = blob.time_created.strftime("%b %d, %Y, %I:%M:%S %p") if blob.time_created else "Unknown"
            updated = blob.updated.strftime("%b %d, %Y, %I:%M:%S %p") if blob.updated else "Unknown"
            
            # Blobs don't have is_public attribute directly - set to Not public by default
            # Getting ACL can cause additional permissions issues
            is_public = False
                
            file_info = {
                "Name": blob.name,
                "Size": format_size(blob.size),
                "Size_Bytes": blob.size,
                "Type": get_content_type(blob),
                "Created": created,
                "Storage_Class": blob.storage_class,
                "Last_Modified": updated,
                "Public_Access": "Public" if is_public else "Not public",
                "Generation": blob.generation,
                "Encryption": blob.kms_key_name if blob.kms_key_name else "Google-managed",
            }
            
            results.append(file_info)
            
            if verbose:
                print(f"{blob.name:<50} {format_size(blob.size):<15} {get_content_type(blob):<20} "
                    f"{created:<25} {blob.storage_class if blob.storage_class else 'Standard':<15} {updated:<25}")
        
        print("\nSummary:")
        print(f"Total files analyzed: {len(blobs)}" + (f" (of {total_file_count} total for this date)" if limit and total_file_count > limit else ""))
        print(f"Total size: {format_size(total_size)}")
        
        if export_csv and results:
            df = pd.DataFrame(results)
            output_file = f"gcs_analysis_{bucket_name.replace('/','-')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(output_file, index=False)
            print(f"\nResults exported to {output_file}")
        
        return results
        
    except Exception as e:
        print(f"Error analyzing bucket: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Google Cloud Storage Bucket Analysis Tool")
    parser.add_argument("bucket_name", help="Name of the GCS bucket to analyze")
    parser.add_argument("--folder", help="Folder/prefix within the bucket")
    parser.add_argument("--limit", type=int, help="Limit the number of files to analyze")
    parser.add_argument("--prefix", help="Filter objects by prefix")
    parser.add_argument("--date", help="Filter by date (format: MM-DD-YYYY)")
    parser.add_argument("--export", action="store_true", help="Export results to CSV")
    parser.add_argument("--verbose", action="store_true", help="Show detailed file listing")
    
    args = parser.parse_args()
    
    # Handle gs:// format if provided
    bucket_name = args.bucket_name
    if bucket_name.startswith("gs://"):
        bucket_name = bucket_name[5:]
    
    # Combine folder with prefix if provided
    prefix = args.prefix
    if args.folder:
        if prefix:
            prefix = f"{args.folder}/{prefix}"
        else:
            prefix = args.folder
    
    analyze_gcs_bucket(bucket_name, args.limit, prefix, args.date, args.export, args.verbose)

if __name__ == "__main__":
    main()