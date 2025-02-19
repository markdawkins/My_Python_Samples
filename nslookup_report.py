import socket
import csv

# Function to perform nslookup and return IP address
def nslookup(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return "Lookup Failed"

# Main function to handle user input and generate the report
def main():
    # Get the file containing hostnames from the user
    file_path = input("Enter the path to the file containing hostnames: ")
    
    # Read hostnames from file
    try:
        with open(file_path, 'r') as f:
            hostnames = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Error: File not found.")
        return
    
    # Output file name
    output_file = "nslookup_report.csv"
    
    # Open CSV file for writing
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header row
        writer.writerow(["Hostname", "IP Address"])
        
        # Perform nslookup for each hostname and write results to CSV
        for host in hostnames:
            ip_address = nslookup(host)
            writer.writerow([host, ip_address])
            print(f"{host}: {ip_address}")
    
    # Notify user that the report has been saved
    print(f"Report saved to {output_file}")

# Run the script if executed directly
if __name__ == "__main__":
    main()
