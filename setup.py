"""
setup for nsupdate package
"""

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme_content = f.read()

setup(
    name='nsupdate',
    version='0.0.1a0',
    url='http://github.com/asmaps/nsupdate.info/',
    license='BSD',
    author='The nsupdate.info Team (see AUTHORS)',
    author_email='info@nsupdate.info',
    description='A dynamic DNS update service',
    long_description=readme_content,
    keywords="dyndns ddns dynamic dns django",
    packages=find_packages(exclude=['_tests', ]),
    package_data={
        'nsupdate.nsupdate.static': ['*', ],
        'nsupdate.nsupdate.templates': ['*', ],
        'nsupdate.main.static': ['*', ],
        'nsupdate.main.templates': ['*', ],
        'nsupdate.accounts.static': ['*', ],
        'nsupdate.accounts.templates': ['*', ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'django<1.6',
        'dnspython',
        'south',
        'django-bootstrap-form',
        'django-registration',
        # packages only needed for development:
        'django-debug-toolbar',
        'pytest',
        'pytest-django',
        'pytest-pep8',
        'sphinx',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: Name Service (DNS)',
    ],
)
