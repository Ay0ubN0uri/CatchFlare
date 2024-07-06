import csv
import sys
from cloudflare import CloudFlare
from cloudfront import CloudFront
from censys_search import CensysSearch
from dotenv import load_dotenv
import os
from securitytrails import SecurityTrails
from utils import colored, is_valid_domain
import cli

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
config = {
    'http_timeout_seconds': 3,
    'response_similarity_threshold': 0.9
}

CERT_CHUNK_SIZE = 25

def filter_cloudflare_ips(ips,cloudflare: CloudFlare):
    return [ ip for ip in ips if not cloudflare.is_cloudflare_ip(ip) ]


# Removes any Cloudfront IPs from the given list
def filter_cloudfront_ips(ips,cloudfront: CloudFront):
    return [ ip for ip in ips if not cloudfront.is_cloudfront_ip(ip) ]


def main(domain, output_file, censys_api_id, censys_api_secret, use_cloudfront, securitytrails_api_key, print_historical_data, method):
    cloudflare = CloudFlare()
    cloudfront = CloudFront()
    if not is_valid_domain(domain):
        sys.stderr.write(colored('[-] The domain "%s" looks invalid.\n' % domain,'red'))
        exit(1)

    if not use_cloudfront:
        if not cloudflare.is_behind_cloudflare(domain):
            print(colored('[-] The domain "%s" does not seem to be behind CloudFlare.' % domain,'red'))
            exit(0)

        print(colored('[+] The target appears to be behind CloudFlare.','green'))

    else: 
        if not cloudfront.is_behind_cloudfront(domain):
            print(colored('[-] The domain "%s" does not seem to be behind CloudFront.' % domain,'red'))
            exit(0)

        print(colored('[*] The target appears to be behind CloudFront.','green'))
    
    if print_historical_data:
        securitytrails = SecurityTrails(securitytrails_api_key)
        print(colored('[*] Printing historical data for %s...' % domain,'green'))
        securitytrails.print_history_table(domain)

    censys_search = CensysSearch(cloudflare,cloudfront,censys_api_id,censys_api_secret)
    if method == 'method1':
        certs = censys_search.get_certificates(domain)
        hosts = censys_search.get_hosts(certs)
        if len(hosts) > 0:
            print(colored('[*] Found %d likely origin servers of %s!' % (len(hosts), domain),'green'))
            for host in hosts:
                print('  - %s (%s)' % (host[0], host[1]))
            if output_file is not None:
                with open(output_file, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['IP', 'Organization', 'Services'])
                    for host in hosts:
                        writer.writerow(host)
        else:
            print(colored('[-] No results found','red'))
    elif method == 'method2':
        if output_file is not None:
            censys_search.get_hosts_method2(domain, output_file)
        else:
            censys_search.get_hosts_method2(domain)

    


if __name__ == "__main__":
    load_dotenv()
    args = cli.parser.parse_args()
    censys_api_id = None
    censys_api_secret = None
    securitytrails_api_key = None
    if 'CENSYS_API_ID' in os.environ and 'CENSYS_API_SECRET' in os.environ and 'SECURITYTRAILS_API_KEY' in os.environ:
        censys_api_id = os.environ['CENSYS_API_ID']
        censys_api_secret = os.environ['CENSYS_API_SECRET']
        securitytrails_api_key = os.environ['SECURITYTRAILS_API_KEY']

    if args.censys_api_id and args.censys_api_secret and args.securitytrails_api_key:
        censys_api_id = args.censys_api_id
        censys_api_secret = args.censys_api_secret
        securitytrails_api_key = args.securitytrails_api_key

    if None in [ censys_api_id, censys_api_secret, securitytrails_api_key ]:
        sys.stderr.write('[!] Please set your Censys API credentials using the CENSYS_API_ID, CENSYS_API_SECRET, and SECURITYTRAILS_API_KEY environment variables. Exiting.\n')
        exit(1)
    main(args.domain, args.output_file, censys_api_id, censys_api_secret, args.use_cloudfront, securitytrails_api_key, args.print_historical_data, args.method)