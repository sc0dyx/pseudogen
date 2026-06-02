from setuptools import setup, find_packages

setup(
    version="0.2.0",
    name="pseudogen",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "pseudogen = pseudogen:main",
        ]
    },
)

