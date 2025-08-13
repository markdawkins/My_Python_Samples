import csv
import subprocess
import sys
import os

# Input file containing IP addresses (adjust path if needed)
INPUT_FILE = "ip_list.csv"

# Output files
OUTPUT_FILE_NS1 = "ns1_results.csv"
OUTPUT_FILE_NS3 = "ns3_results.csv"

# DNS servers
DNS1 = "10.211.1.3"   # ns1.testserver.com
DNS3 = "10.212.64.67" # ns3.testserver.com

def nslookup(ip, dns_server):
    """
    Perform nslookup for a given IP using the specified DNS server.
    Returns the resolved name or 'Not Found' if it fails.
    """
    try:
        result = subprocess.run(
            ["nslookup", ip, dns_server],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout
        for line in output.splitlines():
            if "name =" in line:
                return line.split("name =")[-1].strip()
        return "Not Found"
    except Exception as e:
        return f"Error: {e}"

def process_nslookup(dns_server, output_file):
    """
    Read IPs from CSV and perform nslookup for each IP using dns_server.
    Save results to output_file.
    """
    results = []
    with open(INPUT_FILE, "r") as infile:
        reader = csv.reader(infile)
        for row in reader:
            ip = row[0].strip()
            if ip:
                resolved_name = nslookup(ip, dns_server)
                results.append([ip, resolved_name])

    # Write results to output CSV
    with open(output_file, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["IP Address", "Resolved Name"])
        writer.writerows(results)

def main():
    print("\n========== Script Starting ==========\n")

    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file '{INPUT_FILE}' not found!")
        sys.exit(1)

    # Process for ns1
    print(f"Processing lookups using DNS server {DNS1}...")
    process_nslookup(DNS1, OUTPUT_FILE_NS1)
    print(f"Results saved to {OUTPUT_FILE_NS1}")

    # Process for ns3
    print(f"Processing lookups using DNS server {DNS3}...")
    process_nslookup(DNS3, OUTPUT_FILE_NS3)
    print(f"Results saved to {OUTPUT_FILE_NS3}")

    print("\n========== All completed ==========\n")

if __name__ == "__main__":
    main()
