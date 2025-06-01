import pandas as pd
import argparse

def compare_views(file1, file2, output_file):
    """
    Compare view counts between two CSV files by title and calculate differences.
    
    Args:
        file1 (str): Path to first CSV file
        file2 (str): Path to second CSV file 
        output_file (str): Path for output CSV file
    """
    # Read both CSV files into DataFrames
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Merge DataFrames on 'Title' column
    # Keep all titles from both files (how='outer')
    # Fill NaN values with 0 for missing titles
    merged_df = pd.merge(
        df1, 
        df2, 
        on='Title', 
        how='outer', 
        suffixes=('_file1', '_file2')
    ).fillna(0)

    # Calculate view difference (file2 - file1)
    merged_df['Views_diff'] = merged_df['Views_file2'] - merged_df['Views_file1']

    # Sort by absolute difference in descending order
    result = merged_df.sort_values(
        by='Views_diff', 
        key=lambda x: x.abs(),  # Sort by absolute value
        ascending=False
    )[['Title', 'Views_diff']]  # Select only these columns

    # Save results to CSV
    result.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    # Configure command line argument parser
    parser = argparse.ArgumentParser(
        description='Compare view counts between two CSV files and calculate differences'
    )
    parser.add_argument('file1', help='Path to first CSV file')
    parser.add_argument('file2', help='Path to second CSV file')
    parser.add_argument(
        '-o', 
        '--output', 
        default='views_diff.csv', 
        help='Output CSV filename (default: views_diff.csv)'
    )
    
    # Parse command line arguments
    args = parser.parse_args()

    # Execute comparison
    compare_views(args.file1, args.file2, args.output)