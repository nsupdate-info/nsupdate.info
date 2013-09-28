from setuptools import setup

with open('README.md') as f:
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
    packages=['nsupdate'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'django',
        'dnspython',
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
