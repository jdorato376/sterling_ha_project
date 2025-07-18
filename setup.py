from setuptools import setup, find_packages

setup(
    name="sterling_ha_project",
    version="0.1.0",
    packages=find_packages(include=["modules", "modules.*"]),
    install_requires=[
        # … your deps …
    ],
)
