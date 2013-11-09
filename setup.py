"""
setup for nsupdate package
"""

from setuptools import setup, find_packages

from nsupdate import version

with open('README.rst') as f:
    readme_content = f.read()

setup(
    name='nsupdate',
    version=str(version),
    url='http://github.com/nsupdate-info/nsupdate.info/',
    license='BSD',
    author='The nsupdate.info Team (see AUTHORS)',
    author_email='info@nsupdate.info',
    description='A dynamic DNS update service',
    long_description=readme_content,
    keywords="dyndns ddns dynamic dns django",
    packages=find_packages(exclude=['_tests', ]),
    package_data={
        'nsupdate': [
            'templates/*.html',
            'templates/includes/*.html',
            'static/*.html',
            'static/*.png',
            'static/css/*.css',
        ],
        'nsupdate.accounts': [
            'templates/accounts/*.html',
            'templates/registration/*.html',
            'templates/registration/*.txt',
        ],
        'nsupdate.main': [
            'templates/main/*.html',
            'templates/main/includes/*.html',
        ],
    },
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'django >1.5.3, <1.6',  # 1.5.3 has the session serializer configurable
        'dnspython',
        'south',
        'django-bootstrap-form',
        'django-registration',
        'django-extensions',
        'python-social-auth',
        # packages only needed for development:
        'django-debug-toolbar',
        'pytest',
        'pytest-django',
        'pytest-pep8',
        'sphinx',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: Name Service (DNS)',
    ],
)
