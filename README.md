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
By default resweb will try to connect to redis on localhost. However, if you'd like to connect to another server, create an environment variable called RESWEB_SETTINGS and in the file referenced, put an entry for the following settings:

	RESWEB_HOST = "10.0.0.1:5367"
	RESWEB_PASSWORD = 'somepass'

If you would like to run the server on something other than 127.0.0.1:5000, please set the following variables in the configuration file:

    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 8080

###Authentication Configuration
If you would like to enable basic auth, enable the following settings:

	BASIC_AUTH = True
	AUTH_USERNAME = "someuser"
	AUTH_PASSWORD = "somepassword"
	
Then, use the username and password to login via the authentication popup provided by the browser. Be warned, this is just a stopgap and should not be considered secure.

##Running
After installing, just run the following from the command line:

	resweb 

Afterwards vist: http://localhost:5000

