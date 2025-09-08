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

    # Create timestamped output file names
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_output = f"{timestamp}_comparison_results.txt"
    csv_output = f"{timestamp}_comparison_results.csv"

    with open(txt_output, "w") as f:
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

            # Build structured list of differences
            differences = []
            for row_idx in comparison.index:
                for col in comparison.columns.levels[0]:
                    val1 = comparison.loc[row_idx, (col, "self")]
                    val2 = comparison.loc[row_idx, (col, "other")]
                    if pd.notna(val1) or pd.notna(val2):
                        differences.append({
                            "Row": row_idx,
                            "Column": col,
                            "File1_Value": val1,
                            "File2_Value": val2
                        })
                        # Write to text file in readable format
                        f.write(f"Row {row_idx}, Column '{col}': File1 = {val1}, File2 = {val2}\n")

            # Export to CSV for Excel filtering
            diff_df = pd.DataFrame(differences)
            diff_df.to_csv(csv_output, index=False)

            print(f"Differences found. Results written to:\n  {txt_output}\n  {csv_output}")

if __name__ == "__main__":
    main()
