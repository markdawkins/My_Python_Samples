import os
import time
import csv
import subprocess

def ping_host(host):
    """Ping a host once and return the result."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return "Success"
        else:
            return "Failure"
    except Exception as e:
        return f"Error: {e}"

def main():
    input_directory = "c:\\lists"
    output_directory = "c:\\reports"
    
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Prompt the user for the input file
    input_filename = input(f"Enter the filename (located in {input_directory}): ")
    input_filepath = os.path.join(input_directory, input_filename)

    # Check if the file exists
    if not os.path.isfile(input_filepath):
        print(f"Error: The file {input_filepath} does not exist.")
        return

    # Read the file and process the entries
    output_filepath = os.path.join(output_directory, "ping_results.csv")
    with open(input_filepath, "r") as infile, open(output_filepath, "w", newline="") as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(["IP/Hostname", "Result"])

        for line in infile:
            entry = line.strip()
            if entry:  # Skip empty lines
                result = ping_host(entry)
                csv_writer.writerow([entry, result])
                print(f"Pinged {entry}: {result}")

    print(f"Results have been written to {output_filepath}")
    
    # Wait for 10 seconds
    time.sleep(10)
    print("Script Complete")

if __name__ == "__main__":
    main()
