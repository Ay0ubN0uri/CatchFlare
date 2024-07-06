import requests
from utils import colored
from tabulate import tabulate

class SecurityTrails:
    SECURITYTRAILS_URL = 'https://api.securitytrails.com/v1'
    def __init__(self, securitytrails_api_key):
        self.securitytrails_api_key = securitytrails_api_key
        
    
    def print_history_table(self, domain):
        table_headers = [
            colored('IP Addresses', 'blue', bold=True),
            colored('Organization', 'blue', bold=True),
            colored('First Seen', 'blue', bold=True),
            colored('Last Seen', 'blue', bold=True),
        ]
        url = f"{SecurityTrails.SECURITYTRAILS_URL}/history/{domain}/dns/a"
        headers = {
            "accept": "application/json",
            "APIKEY": self.securitytrails_api_key
        }

        response = requests.get(url, headers=headers)
        result = response.json()
        data = []
        for row in result['records']:
            data.append([
                colored('\n'.join([value['ip'] for value in row['values']]), 'white'),
                colored(','.join(row['organizations']), 'white'),
                colored(row['first_seen'], 'white'),
                colored(row['last_seen'], 'white'),
            ])
        
        print(tabulate(data, table_headers, tablefmt="grid"))
            
        
        
