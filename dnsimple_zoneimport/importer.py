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


class Importer(object):

    def __init__(self, zonefile, email, api_token):
        self.zonefile = zonefile
        self.headers = {
            'X-DNSimple-Token': '{}:{}'.format(email, api_token),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self.domain = self._find_domain()

    def _abort(self, msg):
        logging.error(msg)
        sys.exit(1)

    def _find_domain(self):
        """Try to find out what domain a zonefile belongs to.

        Returns:
            The domain name (no dot at the end).

        Raises:
            LookupError:
                Raised when no domain name can be found.

        """
        if self.zonefile.endswith('.db'):
            basename = self.zonefile.rstrip('.db')
            return basename.rsplit('/', 1)[-1]
        with open(self.zonefile, 'r') as zf:
            for line in zf.xreadlines():
                match = re.match(r'^\s*\$ORIGIN\s*([\w\.]+)\.', line, re.UNICODE)
                if match:
                    return match.groups()[0]
        raise LookupError('Could not find domain name for zone file "{}".'.format(self.zonefile))

    def create_domain(self):
        """Check whether a domain already exists, create it otherwise.

        If a domain already exists, the user is asked whether he wants to continue.
        If he chooses no, exit the program with an error return code.

        """
        url = '{}/domains/'.format(API_ENDPOINT)
        r1 = requests.get(url + self.domain, headers=self.headers)

        if r1.status_code == 200:
            msg = 'Warning: Domain "{}" already exists. Continue anyways? (Y/n) '
            cont = raw_input(msg.format(self.domain)).lower().strip() in ['', 'y', 'yes']
            if cont is False:
                self._abort('Aborting.')
        elif r1.status_code == 404:
            data = {'domain': {'name': self.domain}}
            r2 = requests.post(url, data=json.dumps(data), headers=self.headers)
            r2.raise_for_status()
            logging.info('Created new domain "{}" on DNSimple.'.format(self.domain))
        elif r1.status_code == 401:
            msg = 'Could not access the API (HTTP 401). Are your credentials wrong?'
            self._abort(msg)
        else:
            msg = 'Could not access the API (HTTP {})'.format(r1.status_code)
            self._abort(msg)


    def import_to_dnsimple(self):
        """Actually import the zone file.
        
        If an error occurs, the program exits with an error code.

        """
        logging.info('Importing zonefile {}.'.format(self.zonefile))
        logging.debug('Using headers {!r}'.format(self.headers))
        with open(self.zonefile, 'r') as zf:
            # Import zonefile
            url = '{}/domains/{}/zone_imports'.format(API_ENDPOINT, self.domain)
            data = {'zone_import': {'zone_data': ''.join(zf.readlines())}}
            logging.debug('POSTing to "{}"'.format(url))
            r = requests.post(url, data=json.dumps(data), headers=self.headers)
            if r.status_code != requests.codes.created:
                self._abort('Could not import the zone file (HTTP {})'.format(r.status_code))
            data = r.json()

            # Check number of successful records
            imported_records_count = data['zone_import']['imported_records_count']
            logging.info('Successfully imported {} records.'.format(imported_records_count))

            # Check number of unsuccessful records
            not_imported_records_count = data['zone_import']['not_imported_records_count']
            if not_imported_records_count:
                logging.warning('Could not import {} records.'.format(not_imported_records_count))


def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    requests_log = logging.getLogger('requests.packages.urllib3')
    requests_log.setLevel(logging.WARN)

    # Parse arguments
    arguments = docopt(__doc__, version='v0.1.1')

    # Create and run importer
    importer = Importer(arguments['<zonefile>'], arguments['<email>'], arguments['<api-token>'])
    importer.create_domain()
    importer.import_to_dnsimple()


if __name__ == '__main__':
    main()
