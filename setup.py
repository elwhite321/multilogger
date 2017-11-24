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
    ]
)
