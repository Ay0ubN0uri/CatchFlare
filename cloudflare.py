import requests
import sys
import ipaddress
import dns.resolver
from utils import colored


class CloudFlare:
    def __init__(self,):
        self.cloudflare_ip_ranges_url = 'https://www.cloudflare.com/ips-v4'
        self.ip_ranges = self.get_cloudflare_ip_ranges()
        if sys.version_info[0] == 2:
            self.cloudflare_subnets = [ipaddress.ip_network(ip_range.decode('utf-8')) for ip_range in self.ip_ranges]
        else:
            self.cloudflare_subnets = [ipaddress.ip_network(ip_range) for ip_range in self.ip_ranges]
        
    def get_cloudflare_ip_ranges(self):
        """
        Retrieves the Cloudflare IP ranges from the specified URL.

        This function sends a GET request to the Cloudflare IP ranges URL and retrieves the IP ranges in text format.
        It then splits the text into individual IP ranges and returns them as a list.

        If the request fails, it falls back to a default list of IP ranges.

        Returns:
            list: A list of Cloudflare IP ranges.
        """
        ip_ranges = []
        ip_ranges_fallback = [
            '173.245.48.0/20',
            '103.21.244.0/22',
            '103.22.200.0/22',
            '103.31.4.0/22',
            '141.101.64.0/18',
            '108.162.192.0/18',
            '190.93.240.0/20',
            '188.114.96.0/20',
            '197.234.240.0/22',
            '198.41.128.0/17',
            '162.158.0.0/15',
            '104.16.0.0/13',
            '104.24.0.0/14',
            '172.64.0.0/13',
            '131.0.72.0/22',
        ]
        try:
            print(colored('[*] Retrieving Cloudflare IP ranges from {}'.format(self.cloudflare_ip_ranges_url), 'blue'))
            page_content = requests.get(self.cloudflare_ip_ranges_url, timeout=10)
            ip_ranges_text = page_content.text
            ip_ranges = [ip for ip in ip_ranges_text.split("\n") if ip]

        except requests.exceptions.RequestException:
            sys.stderr.write('[-] Failed to retrieve Cloudflare IP ranges - using a default (possibly outdated) list\n')
            ip_ranges = ip_ranges_fallback
        finally:
            return ip_ranges
    
    def is_cloudflare_ip(self,ip):
        for cloudflare_subnet in self.cloudflare_subnets:
            if cloudflare_subnet.overlaps(ipaddress.ip_network(ip)):
                return True
        return False


    def is_behind_cloudflare(self,domain):
        """
        Check if the given domain is behind Cloudflare.

        Parameters:
            domain (str): The domain to check.

        Returns:
            bool: True if any of the IP addresses returned by the DNS query are within the Cloudflare IP ranges, False otherwise.
        """
        try:
            answers = dns.resolver.resolve(domain, 'A')

            for answer in answers:
                if self.is_cloudflare_ip(answer):
                    return True
            return False
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
            return False

