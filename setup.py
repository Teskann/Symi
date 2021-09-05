from setuptools import setup, find_packages

setup(
    name="Symi",
    description="Command-Line Interface for Symbolic Computation",
    author="Teskann",
    author_email="teskann.dev@protonmail.com",
    url="www.github.com/Teskann/Symi",
    version="0.0.1",
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': ['symi=symi.__main__:main']}
)
