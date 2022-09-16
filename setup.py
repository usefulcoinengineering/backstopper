from setuptools import setup, find_packages

setup(  name='backstopper', 
        version='1.0', 
        summary='gemini backstopper trading bot', 
        homepage='https://www.usefulcoin.com', 
        license=open('LICENSE').read(),
        packages=find_packages(), 
        long_description=open('README.md').read()
)
