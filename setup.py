"""
setup for nsupdate package
"""

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme_content = f.read()

setup(
    name='nsupdate',
    use_scm_version={
        'write_to': 'src/nsupdate/_version.py',
    },
    url='http://github.com/nsupdate-info/nsupdate.info/',
    license='BSD',
    author='The nsupdate.info Team (see AUTHORS)',
    author_email='info@nsupdate.info',
    description='A dynamic DNS update service',
    long_description=readme_content,
    keywords="dyndns ddns dynamic dns django",
    packages=find_packages('src', exclude=['_tests', ]),
    package_dir={'': 'src'},
    # See also the MANIFEST.in file.
    # We want to install all the files in the package directories:
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.7, <3.11',
    setup_requires=['setuptools_scm'],
    install_requires=[
        'dnspython',
        'netaddr',
        'django>=3.2.0',
        'django-bootstrap-form',
        'django-referrer-policy',
        'django-registration-redux',
        'django-extensions',
        'social-auth-app-django',
        'requests',  # for our ddns_client
        'setuptools_scm',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: Name Service (DNS)',
    ],
)
