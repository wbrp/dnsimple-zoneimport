# -*- coding: utf-8 -*-
"""
DNSimple Zone File Importer.

Usage:
    dnsimple_zoneimport -e <email> -t <api-token> <zonefile>
    dnsimple_zoneimport -h | --help
    dnsimple_zoneimport -v | --version

Options:
    -e            DNSimple email address.
    -t            DNSimple API token (see https://dnsimple.com/account).
    -h --help     Show this screen.
    -v --version  Show version.

"""
from __future__ import print_function, division, absolute_import, unicode_literals

import re
import sys
import json
import logging

import requests
from docopt import docopt


API_ENDPOINT = 'https://dnsimple.com'


def build_header(email, api_token, **kwargs):
    """Return a header dictionary for the HTTP requests.

    Args:
        email:
            The DNSimple email address.
        api_token:
            The DNSimple API token (get it at https://dnsimple.com/account).
        **kwargs:
            Any additional headers that you want.

    Returns:
        A header dictionary.

    """
    headers = {
        'X-DNSimple-Token': '{}:{}'.format(email, api_token),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    headers.update(kwargs)
    return headers


def find_domain(zonefile):
    """Try to find out what domain a zonefile belongs to.

    Args:
        zonefile:
            The path to the zonefile as a string.

    Returns:
        The domain name (no dot at the end).

    Raises:
        LookupError:
            Raised when no domain name can be found.

    """
    if zonefile.endswith('.db'):
        basename = zonefile.rstrip('.db')
        return basename.rsplit('/', 1)[-1]
    with open(zonefile, 'r') as zf:
        for line in zf.xreadlines():
            match = re.match(r'^\s*\$ORIGIN\s*([\w\.]+)\.', line, re.UNICODE)
            if match:
                return match.groups()[0]
    raise LookupError('Could not find domain name for zone file "{}".'.format(zonefile))


def create_domain(domain):
    """Check whether a domain already exists, create it otherwise.
    
    If a domain already exists, the user is asked whether he wants to continue.
    If he chooses no, exit the program with an error return code.

    Args:
        domain:
            The domain to create.

    Returns:
        None
    
    """
    url = '{}/domains/'.format(API_ENDPOINT)
    r1 = requests.get(url + domain, headers=headers)
    if r1.status_code == 404:
        data = {'domain': {'name': domain}}
        r2 = requests.post(url, data=json.dumps(data), headers=headers)
        r2.raise_for_status()
        logging.info('Created new domain "{}" on DNSimple.'.format(domain))
    else:
        msg = 'Warning: Domain "{}" already exists. Continue anyways? (Y/n) '.format(domain)
        cont = raw_input(msg).lower().strip() in ['', 'y', 'yes']
        if cont is False:
            sys.exit(1)


def import_zonefile(zonefile, headers):
    """Actually import the zone file.

    Args:
        zonefile:
            The filename/filepath of the zone file.
        headers:
            The base HTTP headers that go with the request (e.g. Authentication
            or Accept headers).

    Returns:
        False if an error occured, True otherwise.

    """
    logging.info('Importing zonefile {}.'.format(zonefile))
    logging.debug('Using headers {!r}'.format(headers))
    with open(zonefile, 'r') as zf:
        # Find domain name
        domain = find_domain(zonefile)

        # Create domain on DNSimple if necessary
        create_domain(domain)

        # Import zonefile
        url = '{}/domains/{}/zone_imports'.format(API_ENDPOINT, domain)
        data = {'zone_import': {'zone_data': ''.join(zf.readlines())}}
        logging.debug('POSTing to "{}"'.format(url))
        r = requests.post(url, data=json.dumps(data), headers=headers)
        if r.status_code != requests.codes.created:
            logging.error('Could not import the zone file (HTTP {})'.format(r.status_code))
            return False
        data = r.json()

        # Check number of successful records
        imported_records_count = data['zone_import']['imported_records_count']
        logging.info('Successfully imported {} records.'.format(imported_records_count))

        # Check number of unsuccessful records
        not_imported_records_count = data['zone_import']['not_imported_records_count']
        if not_imported_records_count:
            logging.warning('Could not import {} records.'.format(not_imported_records_count))

        return True


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.WARN)

    # Parse arguments
    arguments = docopt(__doc__, version='v0.1.0')

    # Build headers, import zonefile
    headers = build_header(arguments['<email>'], arguments['<api-token>'])
    status = import_zonefile(arguments['<zonefile>'], headers)
    sys.exit(0 if status is True else 1)
