DNSimple Zone File Importer
===========================

This script allows you to import a Bind zone file into your DNSimple account.


Installing
----------

To install current version using pip, issue::

    $ sudo pip install dnsimple-zoneimport


Usage
-----

``dnsimple_zoneimport --help``::

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


Testing
-------

To test, the pytest library is required::

    $ pip install pytest

Then run the tests::

    $ py.test


Sourcecode
----------

The sourcecode is available on Github: https://github.com/wbrp/dnsimple-zoneimport


License
-------

The code is licensed under the MIT license. See `LICENSE` file for more details.
