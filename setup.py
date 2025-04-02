from setuptools import setup, find_packages

# Read version from file without importing the module
version_ns = {}
with open("cocotbext/uart/version.py") as f:
    exec(f.read(), version_ns)

setup(
    name="cocotbext-uart",
    version=version_ns["__version__"],
    packages=find_packages(),
    install_requires=["cocotb>=1.4"],
)

