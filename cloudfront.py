import requests
import dns.resolver
import ipaddress
import sys

from utils import colored


class CloudFront:
    def __init__(self,):
        self.cloudfront_ip_ranges_url = 'https://d7uri8nf7uskq.cloudfront.net/tools/list-cloudfront-ips'
        self.cloudfront_backup_ip_ranges_url = 'https://ip-ranges.amazonaws.com/ip-ranges.json'
        self.ip_ranges = self.get_cloudfront_ip_ranges()
    
    def get_cloudfront_ip_ranges(self,):
        ip_ranges = []

        try:
            print(colored('[*] Retrieving Cloudfront IP ranges from {}'.format(self.cloudfront_ip_ranges_url),'blue'))
            page_content = requests.get(self.cloudfront_ip_ranges_url, timeout=10)
            ip_ranges_json = page_content.json()
            ip_ranges = sorted({x for v in ip_ranges_json.values() for x in v})

        except requests.exceptions.RequestException:
            sys.stderr.write('[-] Failed to retrieve Cloudfront IP ranges from cloudfront - trying alternate source')

            try:
                print('[*] Retrieving Cloudfront IP ranges from {}'.format(self.cloudfront_backup_ip_ranges_url))
                page_content = requests.get(self.cloudfront_backup_ip_ranges_url, timeout=10)
                ip_ranges_json = page_content.json()
                filtered_v4_ip_ranges = [x['ip_prefix'] for x in ip_ranges_json['prefixes'] if x['service'] == 'CLOUDFRONT']
                filtered_v6_ip_ranges = [x['ipv6_prefix'] for x in ip_ranges_json['ipv6_prefixes'] if x['service'] == 'CLOUDFRONT']
                ip_ranges = filtered_v4_ip_ranges + filtered_v6_ip_ranges
            except requests.exceptions.RequestException:
                sys.stderr.write('[-] Failed to retrieve Cloudfront IP ranges')
                print('Exiting.')
                exit(1)

        return ip_ranges

    def is_cloudfront_ip(self,ip):
        """
        Check if the given IP address is within the Cloudfront IP ranges.

        Parameters:
            ip (str): The IP address to check.

        Returns:
            bool: True if the IP address is within the Cloudfront IP ranges, False otherwise.
        """
        if sys.version_info[0] == 2:
            self.cloudfront_subnets = [ipaddress.ip_network(ip_range.decode('utf-8')) for ip_range in self.ip_ranges]
        else:
            self.cloudfront_subnets = [ipaddress.ip_network(ip_range) for ip_range in self.ip_ranges]

        for cloudfront_subnet in self.cloudfront_subnets:
            if cloudfront_subnet.overlaps(ipaddress.ip_network(ip)):
                return True
        return False


    def is_behind_cloudfront(self,domain):
        """
        Check if the given domain is behind CloudFront.

        Parameters:
            domain (str): The domain to check.

        Returns:
            bool: True if any of the IP addresses returned by the DNS query are within the CloudFront IP ranges, False otherwise.
        """
        try:
            answers = dns.resolver.query(domain, 'A')

            for answer in answers:
                if self.is_cloudfront_ip(answer):
                    return True

            return False
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
            return False
