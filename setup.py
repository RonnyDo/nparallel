import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Nparallel",        	 
    version="0.1.0",          
    author='Ronny Dobra',
    description='Speed up Nmap scans by running them in parallel',
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer='Ronny Dobra',
    url='https://github.com/RonnyDo/nparallel',
    project_urls={
        'Documentation': 'https://nmap.readthedocs.io/en/latest/',
        'How it is used': 'https://github.com/RonnyDo/nparallel/README.md',
        'Source': 'https://github.com/RonnyDo/nparallel',
    },
    packages=["nparallel"],  	# name of the folder relative to this file where the source code lives
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points = {            # this here is the magic that binds your function into a callable script
        'console_scripts': ['nparallel=nparallel:main'],
    }
)
