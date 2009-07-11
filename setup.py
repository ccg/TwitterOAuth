from distutils.core import setup

setup(
    name="twitter_oauth",
    version="0.1",
    packages=['twitter_oauth'],
    # no dependencies without setuptools...
    #install_requires = ['oauth>=1.0'],
    author='Chad Glendenin',
    author_email='chad@glendenin.com',
    description='Twitter OAuth client',
    license='GPL',
    keywords='twitter oauth',
    url='http://github.com/ccg/twitter_oauth/tree/master',
)
