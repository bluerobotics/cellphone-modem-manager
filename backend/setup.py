import os
import ssl

from setuptools import setup, find_packages

# Ignore ssl if it fails
if not os.environ.get("PYTHONHTTPSVERIFY", "") and getattr(ssl, "_create_unverified_context", None):
    ssl._create_default_https_context = ssl._create_unverified_context

setup(
    name="lte_eg25_g",
    version="0.1.0",
    description="Simple extension to manager LT EG35-G modem",
    license="MIT",
    packages=find_packages(include=['api']),
    install_requires=[
        "appdirs==1.4.4",
        "fastapi==0.115.3",
        "fastapi-versioning==0.10.0",
        "loguru == 0.5.3",
        "pydantic==2.9.2",
        "pyserial==3.5",
        "uvicorn==0.32.0",
    ],
)
