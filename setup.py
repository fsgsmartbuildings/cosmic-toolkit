from setuptools import setup, find_packages

VERSION = "0.4.0"


with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="cosmic-toolkit",
    version=VERSION,
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=[
        "pydantic==1.7.1",
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
