from setuptools import find_packages, setup

setup(
    name='simple-json-logging',
    packages=find_packages(),
    license='MIT',
    version='1.0.1',
    author='Sergey Nevmerzhitsky',
    author_email='sergey.nevmerzhitsky@gmail.com',
    url='https://github.com/nevmerzhitsky/python-simple-json-logging',
    download_url='https://github.com/nevmerzhitsky/python-simple-json-logging/archive/v1.0.1.tar.gz',
    description='Library for structured logging via JSON document',
    install_requires=[
        'pytest>=3.7.0'
    ],
    keywords=['logging', 'json'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
)
