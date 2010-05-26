from distutils.core import setup

setup(
    name='openallure',
    version='0.1d14',
    author='John Graves',
    author_email='john.graves@aut.ac.nz',
    packages=['openallure'],
    url='http://openallureds.org',
    license='LICENSE.txt',
    description='Voice-and-vision enabled dialog system',
    platforms=['Windows','Linux','Mac'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Multimedia :: Video :: Capture',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces'
        ],
    long_description=open('README.txt').read()
)