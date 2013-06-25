# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from dnsimple_zoneimport import meta

f = open('requirements.txt', 'r')
lines = f.readlines()
requirements = [l.strip().strip('\n') for l in lines if l.strip() and not l.strip().startswith('#')]
readme = open('README.rst').read()

setup(name='dnsimple-zoneimport',
      version=meta.version,
      description=meta.description,
      author=meta.author,
      author_email=meta.author_email,
      url='https://github.com/wbrp/dnsimple-zoneimport',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      license=meta.license,
      keywords='dnsimple dns "zone files" bind import api',
      long_description=readme,
      install_requires=requirements,
      entry_points={
          'console_scripts': [
              '%s = dnsimple_zoneimport.importer:main' % meta.title.replace('-', '_'),
          ]
      },
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'License :: OSI Approved :: MIT License',
          'Natural Language :: English',
          'Operating System :: MacOS',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: Name Service (DNS)',
          'Topic :: Terminals',
      ],
)
