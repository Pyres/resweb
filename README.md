Resweb
======
##About
Resweb originally started as part of the pyres project. However, I realized that for many reasons, both it and pyres would benefit 
from being their own projects. Hopefully this will help the release schedule of both pyres and resweb.

##Installation
* pip install resweb
or
* download source and run: python setup.py install

##Configuration
By default resweb will try to connect to redis on localhost. However, if you'd like to connect to another server, create and env variable called RESWEB_SETTINGS and in the file referenced, but an entry for PYRES_HOST:

	PYRES_HOST_HOST = "10.0.0.1:5367"
	
##Running
After installing, just run the following from the command line:

	resweb 

Afterwards vist: http://localhost:5000
