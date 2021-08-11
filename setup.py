#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#


import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="open-jarvis", # Replace with your own username
    version="0.1.7",
    author="Philipp Scheer",
    author_email="scheer28philipp@gmail.com",
    description="Helper classes for Jarvis applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/open-jarvis",
    packages=setuptools.find_packages(),
    install_requires=[
        'paho.mqtt; platform_machine == "armv7l"',
        'couchdb2',
        'python-dateutil'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires='>=3.6',
)


