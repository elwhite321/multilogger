from setuptools import setup, find_packages

setup(
    name="multilogger",
    version="0.0.1",
    description="slack and combined logger",
    author="Eric White",
    url="https://github.com/18Birdies",
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    install_requires=[
        "slackclient",
        "datalib"
    ],
    dependency_links=[
        "git+https://25ad56ade1f65a65182c4cc04f549a03b934bcef@github.com/18Birdies/data-library#egg=datalib-1.0.0"
    ]
)
