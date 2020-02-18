# simplewebserver
A simple web server written in Python.

### Features:
  * Serving web pages (including static files)
  * Directory listing (can be configured in settings)
  * Logging (can be configured in settings)
  * Content compression
  * Custom 404 and directory listing pages

### How it works
simplewebserver is a multithreaded web server that is abstracted into three parts: requests, responses and files.<br />
The web server listens for connections on a single thread, and then once a connection is received, handles that connection on a separated thread.<br /><br />
The web server then parses the request and ensures that it is in the correct format. If not, it sends the appropriate response indicating that it received a bad request (HTTP 400).<br />
If the request was valid, the web server then determines the path of the requested file. If the path is '/', it looks for an index file by searching through a list of index files configured in settings. If the path is not '/', then it searches for the requested file.<br /><br /> The web server then attempts to serve the file, as well as compressing its contents to save space. If the file does not exist, it sends back an HTTP 404 error. If the requested path is a directory, the web server sends back a directory listing, or a 404 response if the directory does not exist.<br /><br />
After doing all this, the server closes the connection.
