import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument(
    'domain',
    help = 'The target domain to scan'
)

parser.add_argument(
    '-o', '--output',
    help = 'A csv file to output the results',
    dest = 'output_file'
)

parser.add_argument(
    '--censys-api-id',
    help = 'Censys API ID. Can also be defined using the CENSYS_API_ID environment variable',
    dest = 'censys_api_id'
)

parser.add_argument(
    '--censys-api-secret',
    help = 'Censys API secret. Can also be defined using the CENSYS_API_SECRET environment variable',
    dest = 'censys_api_secret'
)

parser.add_argument(
    '--print-historical-data',
    help = 'Print historical data for the domain.',
    dest = 'print_historical_data',
    action='store_true',
    default=False
)

parser.add_argument(
    '--securitytrails-api-key',
    help = 'SecurityTrails API key. Can also be defined using the SECURITYTRAILS_API_KEY environment variable',
    dest = 'securitytrails_api_key'
)

parser.add_argument(
    '--method',
    choices=['method1', 'method2'], 
    default='method1', 
    help='Specify the method to use (method1 or method2)'
)

parser.add_argument(
    '--cloudfront',
    help = 'Check Cloudfront instead of CloudFlare.',
    dest = 'use_cloudfront',
    action='store_true',
    default=False
)