from distutils.core import setup

# place __version__ in setup.py namespace, w/o
# having to import and creating a dependency nightmare
execfile('pyfaceb/version.py')

setup(
    name='pyfaceb',
    version=__version__,
    author='Kevin Stanton',
    author_email='kevin@sproutsocial.com',
    packages=['pyfaceb', 'pyfaceb.test'],
    url='https://bitbucket.org/sproutsocial/pyfaceb',
    license='LICENSE.txt',
    install_requires = ['requests >= 0.10'],
    description='Full-featured, lightweight Facebook API wrapper for Graph & FQL.',
    long_description=open('README.txt').read(),
)
