from setuptools import setup, find_packages

VERSION = "0.5.0"


with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="cosmic-toolkit",
    version=VERSION,
    description="Domain-Driven Design (DDD) toolkit to quickly develop complex apps",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=[
        "orjson>=3.4",
        "pydantic>=1.7",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="cosmic,messagebus,domain driven design,clean architecture"
)
