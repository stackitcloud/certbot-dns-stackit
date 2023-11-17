from setuptools import setup
from setuptools import find_packages
import os

version = os.environ.get("PACKAGE_VERSION", "v0.1.1")

install_requires = [
    "acme>=2.6.0",
    "certbot>=2.6.0",
    "setuptools",
    "requests",
    "mock",
    "requests-mock",
    "mypy",
    "mypy-extensions",
    "types-requests",
    "types-urllib3",
    "flake8",
    "pydocstyle",
    "black",
    "click==8.1.7",
    "coverage",
]

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

setup(
    name="certbot-dns-stackit",
    version=version,
    description="STACKIT DNS Authenticator plugin for Certbot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stackitcloud/certbot-dns-stackit",
    author="STACKIT DNS",
    author_email="stackit-dns@mail.schwarz",
    license="Apache License 2.0",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "certbot.plugins": ["dns-stackit = certbot_dns_stackit.stackit:Authenticator"]
    },
    test_suite="certbot_dns_stackit",
)
