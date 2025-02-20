from setuptools import setup, find_packages

setup(
    name="pygrits",
    version="0.1.0",
    packages=find_packages(include=["app"]),
    install_requires=[
        "click",
        "colorama",
        "pathlib",
    ],
    entry_points={
        "console_scripts": [
            "pygrits=app.cli.commands:cli",  # Changed from pygrits.cli to app.cli
        ],
    },
)