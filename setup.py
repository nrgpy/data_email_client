from setuptools import setup

with open("README.md", "r") as fh:
      long_description = fh.read()

setup(
      name='data_email_client',
      version='0.1.4',
      description='email imap client for downloading email data files',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/nrgpy/data_email_client',
      packages=['data_email_client'],
      author='NRG Systems, Inc.',
      author_email='support@nrgsystems.com',
      keywords='nrg systems rld symphonie symphoniepro wind data spidar remote sensor lidar email imap',
      python_requires='>=3.5',
      zip_safe=False,
      classifiers=[
          'License :: OSI Approved :: MIT License'
      ],
)
