from setuptools import setup, find_packages
from pip.req import parse_requirements

setup(name='d2modeling',
      version='0.2',
      packages=find_packages(exclude=['bin', '.git', 'test', 'examples']),
      zip_safe=False,
      install_requires=[str(requirement.req) for requirement in parse_requirements("./requirements.txt")],
      )
