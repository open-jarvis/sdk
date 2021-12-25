#
# Copyright (c) 2020 by Philipp Scheer. All Rights Reserved.
#


import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="open-jarvis-sdk", # Replace with your own username
    version="0.0.1",
    author="Philipp Scheer",
    author_email="hi@fipsi.at",
    description="Software Development Kit for varius AI tasks including Intent Parsing & more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/open-jarvis/sdk",
    packages=setuptools.find_packages(),
    install_requires=[
        "websocket",
        "requests"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires='>=3.6',
)


