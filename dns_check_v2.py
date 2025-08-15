"""
DNS Resolution Check Script

This script performs DNS resolution checks for a list of hostnames against two nameservers (ns1 and ns9).
It reads hostnames from an Excel file and writes the results to separate CSV files for each nameserver.

Features:
- Reads hostnames from Excel file (first column)
- Performs DNS A record lookups against specified nameservers
- Handles various DNS resolution errors gracefully
- Writes results to CSV files with timestamps
- Shows real-time progress during execution

Requirements:
- Python 3.6+
- Packages: dnspython, openpyxl (install with: pip install dnspython openpyxl)
"""

import dns.resolver  # For DNS resolution
import openpyxl      # For reading Excel files
import csv           # For writing CSV files
from datetime import datetime  # For timestamping results
import sys           # For system exit and stderr

def resolve_hostname(hostname, nameserver):
    """
    Resolve a hostname to its IP addresses using a specific nameserver
    
    Args:
        hostname (str): The hostname to resolve
        nameserver (str): IP address of the nameserver to query
    
    Returns:
        list: List of IP addresses or error messages
    """
    # Create a DNS resolver instance
    resolver = dns.resolver.Resolver()
    # Configure the resolver to use our specific nameserver
    resolver.nameservers = [nameserver]
    
    try:
        # Perform the DNS query for A records
        answers = resolver.resolve(hostname, 'A')
        # Extract and return all IP addresses
        return [str(answer) for answer in answers]
    except dns.resolver.NXDOMAIN:
        return ["NXDOMAIN (Non-existent domain)"]
    except dns.resolver.NoAnswer:
        return ["No A records found"]
    except dns.resolver.Timeout:
        return ["DNS query timed out"]
    except dns.resolver.NoNameservers:
        return ["No working nameservers"]
    except Exception as e:
        return [f"DNS resolution error: {str(e)}"]

def read_hostnames_from_excel(file_path):
    """
    Read hostnames from the first column of an Excel file
    
    Args:
        file_path (str): Path to the Excel file
    
    Returns:
        list: List of hostnames to check
    
    Raises:
        SystemExit: If the file cannot be read
    """
    try:
        # Load the Excel workbook
        workbook = openpyxl.load_workbook(file_path)
        # Get the active worksheet
        sheet = workbook.active
        hostnames = []
        
        # Iterate through all rows in the first column
        for row in sheet.iter_rows(values_only=True):
            if row and row[0]:  # Check if first column has a value
                hostname = str(row[0]).strip()
                # Skip empty lines and lines starting with # (comments)
                if hostname and not hostname.startswith('#'):
                    hostnames.append(hostname)
        
        return hostnames
    except Exception as e:
        print(f"ERROR: Failed to read Excel file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def write_results_to_csv(file_path, results):
    """
    Write DNS resolution results to a CSV file
    
    Args:
        file_path (str): Path to the output CSV file
        results (dict): Dictionary of {hostname: [ip_addresses]}
    
    Raises:
        SystemExit: If the file cannot be written
    """
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header row
            writer.writerow(['Hostname', 'IP Addresses', 'Timestamp'])
            # Write each result row
            for hostname, ips in results.items():
                writer.writerow([
                    hostname, 
                    ', '.join(ips), 
                    datetime.now().isoformat()  # Current timestamp
                ])
    except Exception as e:
        print(f"ERROR: Failed to write CSV file: {str(e)}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main execution function for the script"""
    
    # ===== CONFIGURATION =====
    # Path to the input Excel file
    input_file = r"C:\Users\MGD002\OneDrive - Comerica\Desktop\Sunday_CHG_DOCS\DNSCheckList082025.xlsx"
    
    # Output CSV file paths
    output_ns1 = r"C:\Users\MGD002\OneDrive - Comerica\Desktop\Sunday_CHG_DOCS\DNSCheckList082025-ns1results01.csv"
    output_ns9 = r"C:\Users\MGD002\OneDrive - Comerica\Desktop\Sunday_CHG_DOCS\DNSCheckList082025-ns9results01.csv"
    
    # Nameservers to test against
    dns_servers = {
        'ns1': '10.212.6.64',
        'ns9': '10.211.134.47'
    }
    # ===== END CONFIGURATION =====

    print("\nDNS Resolution Check Script")
    print("=" * 50)
    print(f"Input file: {input_file}")
    print(f"Nameservers: {', '.join(dns_servers.keys())}\n")

    # STEP 1: Read hostnames from Excel
    print("[1/3] Reading hostnames from Excel file...")
    hostnames = read_hostnames_from_excel(input_file)
    if not hostnames:
        print("ERROR: No valid hostnames found in the input file.", file=sys.stderr)
        sys.exit(1)
    
    print(f"Found {len(hostnames)} hostnames to check\n")

    # STEP 2: Perform DNS resolution against each nameserver
    for server_name, server_ip in dns_servers.items():
        print(f"[2/3] Checking against {server_name} ({server_ip})...")
        
        results = {}
        total = len(hostnames)
        
        # Process each hostname
        for i, hostname in enumerate(hostnames, 1):
            # Calculate and display progress
            progress = (i / total) * 100
            print(f"\r  {i}/{total} ({progress:.1f}%) - Resolving: {hostname.ljust(50)}", end='', flush=True)
            
            # Perform DNS resolution
            ips = resolve_hostname(hostname, server_ip)
            results[hostname] = ips
        
        # STEP 3: Write results to CSV
        output_file = output_ns1 if server_name == 'ns1' else output_ns9
        write_results_to_csv(output_file, results)
        print(f"\n  Results saved to: {output_file}\n")

    print("[3/3] Script completed successfully\n")

if __name__ == "__main__":
    # Execute the main function when script is run directly
    main()
