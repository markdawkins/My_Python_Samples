import requests
import urllib3
from getpass import getpass

# Suppress insecure HTTPS warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# F5 connection details
f5_host = input("F5 Management IP or Hostname: ")
username = input("Username: ")
password = getpass("Password: ")
pool_name = input("Enter the pool name to search for: ")

# Base URL for API
base_url = f"https://{f5_host}/mgmt/tm"

# Authentication
session = requests.Session()
session.auth = (username, password)
session.verify = False
session.headers.update({'Content-Type': 'application/json'})

# Find the pool
def find_pool(pool_name):
    url = f"{base_url}/ltm/pool"
    response = session.get(url)
    response.raise_for_status()
    pools = response.json().get('items', [])
    
    for pool in pools:
        if pool['name'] == pool_name:
            print(f"\n✅ Found pool: {pool['name']}")
            return pool
    print(f"\n❌ Pool named '{pool_name}' not found.")
    return None

# List members of the given pool
def list_pool_members(pool_name):
    # Partition is assumed to be /Common unless you specify otherwise
    url = f"{base_url}/ltm/pool/~Common~{pool_name}/members"
    response = session.get(url)
    if response.status_code == 404:
        print(f"\n⚠️  No members found for pool '{pool_name}'.")
        return
    response.raise_for_status()
    members = response.json().get('items', [])

    print(f"\n👥 Members of pool '{pool_name}':")
    for member in members:
        print(f" - {member['name']} (State: {member.get('session', 'unknown')})")

# Main
if __name__ == "__main__":
    pool = find_pool(pool_name)
    if pool:
        list_pool_members(pool_name)
