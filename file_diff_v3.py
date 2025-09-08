import pandas as pd
from datetime import datetime

def main():
    # Prompt user for file paths
    file1 = input("Enter path to File 1 (CSV or Excel): ").strip()
    file2 = input("Enter path to File 2 (CSV or Excel): ").strip()

    # Detect file types and load into DataFrames
    try:
        if file1.endswith(".csv"):
            df1 = pd.read_csv(file1)
        else:
            df1 = pd.read_excel(file1)

        if file2.endswith(".csv"):
            df2 = pd.read_csv(file2)
        else:
            df2 = pd.read_excel(file2)
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    # Check if structure is the same
    if df1.shape != df2.shape or list(df1.columns) != list(df2.columns):
        print("The two files have different structures (columns/rows).")
        return

    # Compare data
    comparison = df1.compare(df2, keep_shape=True, keep_equal=False)

    # Create timestamped output file name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{timestamp}_comparison_results.txt"

    with open(output_file, "w") as f:
        f.write(f"Comparison Results\n")
        f.write(f"File 1: {file1}\n")
        f.write(f"File 2: {file2}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("=" * 60 + "\n\n")

        if comparison.empty:
            f.write("No Differences Found\n")
            print("No Differences Found")
        else:
            f.write("Differences found between files:\n\n")
            f.write(comparison.to_string())
            print(f"Differences found. Results written to {output_file}")

if __name__ == "__main__":
    main()
