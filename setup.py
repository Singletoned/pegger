from setuptools import setup, find_packages

version = '0.1'

setup(
    name='pegger',
    version=version,
    author="Ed Singleton",
    author_email="singletoned@gmail.com",
    description="Some kind of simplistic PEG style parser",
    py_modules=['pegger'],
    include_package_data=True,
    zip_safe=False,
)
