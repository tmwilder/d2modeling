from setuptools import setup, find_packages

setup(name='d2modeling',
      version='0.1',
      packages=find_packages(exclude=['bin', '.git', 'test', 'examples']),
      zip_safe=False,
      install_requires=["SQLAlchemy==0.9.4", "argparse==1.2.1", "beautifulsoup4==4.3.2", "requests==2.3.0"],
      )
