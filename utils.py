import dns.resolver
from fake_useragent import UserAgent
import ipaddress

def is_valid_domain(domain):
    try:
        dns.resolver.query(domain, 'A')
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
        return False


def colored(text, color, bold=False,bg_color=None):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'black': '\033[30m',
    }
    bg_colors = {
        'red': '\033[101m',
        'green': '\033[102m',
        'yellow': '\033[103m',
        'blue': '\033[104m',
        'magenta': '\033[105m',
        'cyan': '\033[106m',
        'white': '\033[107m'
    }
    bold_code = '\033[1m' if bold else ''
    fg_code = colors.get(color, '')
    bg_code = bg_colors.get(bg_color, '')
    return f"{bold_code}{fg_code}{bg_code}{text}{colors['reset']}"


def get_random_user_agent():
    ua = UserAgent()
    return ua.random
    

def is_ipv4(ip):
    try:
        ip_obj = ipaddress.ip_address(ip)
        if isinstance(ip_obj, ipaddress.IPv4Address):
            return True
        return False
    except ValueError:
        return False