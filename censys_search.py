import csv
import sys
from cloudflare import CloudFlare
from cloudfront import CloudFront

from censys.common.exceptions import (
    CensysRateLimitExceededException,
    CensysUnauthorizedException,
)
from censys.search import CensysCerts, CensysHosts
from utils import is_ipv4,colored
from tabulate import tabulate


class CensysSearch:
    
    USER_AGENT = (
        f"{CensysCerts.DEFAULT_USER_AGENT} (CloudFlair; +https://github.com/Ay0ubN0uri/CatchFlare)"
    )
    INVALID_CREDS = "[-] Your Censys credentials look invalid.\n"
    RATE_LIMIT = "[-] Looks like you exceeded your Censys account limits rate. Exiting\n"
    def __init__(self,cloudflare:CloudFlare,cloudfront:CloudFront,censys_api_id,censys_api_secret):
        self.censys_api_id = censys_api_id
        self.censys_api_secret = censys_api_secret
        self.cloudflare = cloudflare
        self.cloudfront= cloudfront
        self.censys_hosts = CensysHosts(
                api_id=self.censys_api_id, api_secret=self.censys_api_secret, user_agent=CensysSearch.USER_AGENT
            )
        self.censys_certificates = CensysCerts(
                api_id=self.censys_api_id, api_secret=self.censys_api_secret, user_agent=CensysSearch.USER_AGENT
            )
    
    def get_hosts(self,cert_fingerprints):
        try:
            hosts_query = f"services.tls.certificates.leaf_data.fingerprint: {{{','.join(cert_fingerprints)}}}"
            hosts_search_results = self.censys_hosts.search(hosts_query).view_all()
            return set(
                [r["ip"] for r in hosts_search_results.values()]
            )
        except CensysUnauthorizedException:
            sys.stderr.write(CensysSearch.INVALID_CREDS)
            exit(1)
        except CensysRateLimitExceededException:
            sys.stderr.write(CensysSearch.RATE_LIMIT)
            exit(1)
    
    def get_certificates(self,domain, pages=2):
        try:

            certificate_query = f"names: {domain} and parsed.signature.valid: true and not names: cloudflaressl.com"
            certificates_search_results = self.censys_certificates.search(
                certificate_query, per_page=100, pages=pages
            )

            fingerprints = set()
            for page in certificates_search_results:
                for cert in page:
                    fingerprints.add(cert["fingerprint_sha256"])
            return fingerprints
        except CensysUnauthorizedException:
            sys.stderr.write(CensysSearch.INVALID_CREDS)
            exit(1)
        except CensysRateLimitExceededException:
            sys.stderr.write(CensysSearch.RATE_LIMIT)
            exit(1)
    
    
    def get_hosts_method2(self, domain, output_file=None):
        results = self.censys_hosts.search(domain).view_all()
        headers = [
            colored('IP', 'blue', bold=True),
            colored('Organization', 'blue', bold=True),
            colored('Services', 'blue', bold=True),
        ]
        data = []
        out_data = []
        for item in results.keys():
            if is_ipv4(item) and not self.cloudflare.is_cloudflare_ip(item) and not self.cloudfront.is_behind_cloudfront(item):
                ip = item
                organization = 'N/A'
                if 'whois' in results[item]:
                    if 'organization' in results[item]['whois']:
                        organization = results[item]['whois']['organization']['name']
                    elif 'network' in results[item]['whois']:
                        organization = results[item]['whois']['network']['name']
                services = 'N/A'
                if 'services' in results[item]:
                    if output_file is not None:
                        out_services = ' - '.join([f'{service["service_name"]}({service["port"]})' for service in results[item]['services']])
                    services = ' - '.join([colored(f'{service["service_name"]}({service["port"]})','white',True) for service in results[item]['services']])
                if output_file is not None:
                    out_data.append([ip, organization, out_services])
                data.append([ip, organization, services])
        if len(data) == 0:
            print(colored('[-] No results found', 'red'))
        else:
            print(colored('[*] Found %d likely origin servers of %s!' % (len(data), domain), 'green'))
            print(tabulate(data, headers, tablefmt="grid"))
            if output_file is not None:
                with open(output_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([
                        'IP',
                        'Organization',
                        'Services'
                    ])
                    writer.writerows(out_data)
                    print(colored('[+] Output saved to %s' % output_file, 'green'))
        
    def test(self,):
        results = self.censys_hosts.search('ultramobile.com')
        print(results.view_all())