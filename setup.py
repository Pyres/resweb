from setuptools import setup, find_packages
version=__import__('resweb').__version__
setup(
    name='resweb',
    version=version,
    description='Pyres web interface',
    author='Matt George',
    author_email='mgeorge@gmail.com',
    maintainer='Matt George',
    license='MIT',
    url='http://github.com/Pyres/resweb',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    download_url='http://pypi.python.org/packages/source/p/resweb/resweb-%s.tar.gz' % version,
    include_package_data=True,
    package_data={'resweb': ['templates/*.mustache','static/*']},
    install_requires=[
        'pyres>=1.3',
        'flask',
        'pystache'
    ],
    entry_points = """\
    [console_scripts]
    resweb=resweb.core:main
    """,
    classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python'],
)
