from setuptools import find_packages, setup

setup(
    name="py-rest-api-client",
    version="0.1.0",
    description="A small, extensible REST API client inspired by RestApiClientSharp",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    install_requires=["requests>=2.25,<2.32"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
