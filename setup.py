from setuptools import setup, find_packages

setup(
    name="bba_data_fetch",
    author="Blue Brain Project, EPFL",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Fetch data for the Blue Brain Atlas Pipeline",
    download_url="git@bbpgitlab.epfl.ch:dke/apps/blue_brain_atlas_data_fetch.git",
    license="BBP-internal-confidential",
    python_requires=">=3.6.0",
    install_requires=[
        "nexus-sdk>=0.3.2",
        "click>=7.0",
        "numpy>=1.19",
        "pynrrd>=0.4.0",
        "nexusforge>=0.8.1",
    ],
    extras_require={
        "dev": ["pytest>=4.3", "pytest-cov==2.10.0"],
    },
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["bba-data-fetch=bba_data_fetch.main:run"]},
)
