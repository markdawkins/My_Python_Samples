import dns.resolver
import openpyxl
import csv
from datetime import datetime
import sys

def resolve_hostname(hostname, nameserver):
    """Resolve a hostname using a specific nameserver"""
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [nameserver]
    
    try:
        answers = resolver.resolve(hostname, 'A')
        return [str(answer) for answer in answers]
    except dns.resolver.NXDOMAIN:
        return ["NXDOMAIN"]
    except dns.resolver.NoAnswer:
        return ["No A records"]
    except dns.resolver.Timeout:
        return ["Timeout"]
    except dns.resolver.NoNameservers:
        return ["No nameservers"]
    except Exception as e:
        return [f"Error: {str(e)}"]

def read_hostnames_from_excel(file_path):
    """Read hostnames from Excel file (first column)"""
    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active
        hostnames = []
        
        for row in sheet.iter_rows(values_only=True):
            if row and row[0]:  # First column value exists
                hostname = str(row[0]).strip()
                if hostname and not hostname.startswith('#'):  # Skip empty lines and comments
                    hostnames.append(hostname)
        
        return hostnames
    except Exception as e:
        print(f"Error reading Excel file: {str(e)}")
        sys.exit(1)

def write_results_to_csv(file_path, results):
    """Write results to CSV file"""
    try:
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Hostname', 'IP Addresses', 'Timestamp'])
            for hostname, ips in results.items():
                writer.writerow([hostname, ', '.join(ips), datetime.now().isoformat()])
    except Exception as e:
        print(f"Error writing to CSV file: {str(e)}")
        sys.exit(1)

def main():
    # Configuration
    input_file = r"C:\Users\MGD002\OneDrive - Comerica\Desktop\Sunday_CHG_DOCS\DNSCheckList082025.xlsx"
    output_ns1 = r"C:\Users\MGD002\OneDrive - Comerica\Desktop\Sunday_CHG_DOCS\DNSCheckList082025-ns1results01.csv"
    output_ns9 = r"C:\Users\MGD002\OneDrive - Comerica\Desktop\Sunday_CHG_DOCS\DNSCheckList082025-ns9results01.csv"
    
    dns_servers = {
        'ns1': '10.212.6.64',
        'ns9': '10.211.134.47'
    }

    print("DNS Resolution Check Script")
    print("=" * 50)

    # Read hostnames from Excel
    print("\nReading hostnames from Excel file...")
    hostnames = read_hostnames_from_excel(input_file)
    if not hostnames:
        print("No valid hostnames found in the input file.")
        sys.exit(1)
    
    print(f"Found {len(hostnames)} hostnames to check")

    # Test against each nameserver
    for server_name, server_ip in dns_servers.items():
        print(f"\nChecking against {server_name} ({server_ip})...")
        
        results = {}
        total = len(hostnames)
        for i, hostname in enumerate(hostnames, 1):
            # Progress indicator
            progress = (i / total) * 100
            print(f"\r[{i}/{total}] {progress:.1f}% - Resolving: {hostname.ljust(50)}", end='')
            
            ips = resolve_hostname(hostname, server_ip)
            results[hostname] = ips
        
        # Write results to CSV
        output_file = output_ns1 if server_name == 'ns1' else output_ns9
        write_results_to_csv(output_file, results)
        print(f"\nResults saved to {output_file}")

    print("\nScript completed successfully")

if __name__ == "__main__":
    main()
