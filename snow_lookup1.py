import requests
from requests.auth import HTTPBasicAuth
import getpass
import csv

# ServiceNow instance details
instance = 'your_instance'  # Replace with your ServiceNow instance

# Prompt for username and password
username = input("Enter your ServiceNow username: ")
password = getpass.getpass("Enter your ServiceNow password: ")

# Function to get user display name from user ID
def get_user_display_name(user_id):
    url = f'https://{instance}.service-now.com/api/now/table/sys_user/{user_id}'
    headers = {
        'Accept': 'application/json'
    }
    response = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers)
    if response.status_code == 200:
        user = response.json().get('result', {})
        return user.get('name', 'N/A')
    else:
        return 'N/A'

# Endpoint URL
url = f'https://{instance}.service-now.com/api/now/table/incident'

# Query parameters to filter incidents assigned to the specific user, sorted by creation date descending
params = {
    'sysparm_query': f'assigned_to.user_name={username}^ORDERBYDESCsys_created_on',
    'sysparm_fields': 'number,short_description,sys_created_on,assigned_to,opened_by,requestor',
    'sysparm_limit': '20'  # Retrieve 20 most recent incidents
}

# Headers
headers = {
    'Accept': 'application/json'
}

# Make the request
response = requests.get(url, auth=HTTPBasicAuth(username, password), headers=headers, params=params)

# Check the response status
if response.status_code == 200:
    # Parse the JSON response
    incidents = response.json().get('result', [])
    
    # CSV file name
    csv_file = 'incidents.csv'
    
    # Writing to CSV
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Number', 'Short Description', 'Created On', 'Opened By', 'Requestor'])
        
        # Write the data
        for incident in incidents:
            number = incident.get('number', 'N/A')
            short_description = incident.get('short_description', 'N/A')
            created_on = incident.get('sys_created_on', 'N/A')

            opened_by = incident.get('opened_by', {}).get('value', 'N/A')
            if opened_by != 'N/A':
                opened_by = get_user_display_name(opened_by)

            requestor = incident.get('requestor', {}).get('display_value', 'N/A')

            writer.writerow([number, short_description, created_on, opened_by, requestor])
    
    print(f"Incidents have been written to {csv_file}")
else:
    print(f"Failed to retrieve incidents. Status code: {response.status_code}, Response: {response.text}")
