import os

from misc import misc

# Server related information
SERVER_ROOT = os.getcwd()
SERVER_NAME = 'WebServer/1.0'

HOST = '127.0.0.1'
PORT = 80

# Directory to search for HTML, CSS and JS files
FILES_DIR = os.path.join(SERVER_ROOT, 'htdocs')

# Allowed HTTP methods
HTTP_METHODS = ['GET', 'POST']

# List of possible index files in root directory
INDEX_FILES = ['index.html', 'index.htm', 'index.shtml']

# Response headers to be sent with each HTTP response
STANDARD_RESPONSE_HEADERS = {
    'Date': misc.get_date(),
    'Server': SERVER_NAME
}

CONNECTION_BACKLOG = 5

# Path to Jinja2 template files
PATH_TO_TEMPLATES = 'config/templates'

# Path to 404.html error template file
PATH_TO_404 = os.path.join(PATH_TO_TEMPLATES, '404.html')

# Path to directory listing template file
PATH_TO_LISTING = os.path.join(PATH_TO_TEMPLATES, 'listing.html')

# Logging
LOGGING_ENABLED = True

# Log file to log HTTP requests to
LOG_FILE = 'log.txt'

# Directory listing options
DIRECTORY_LISTING_ENABLED = True
NOINDEX_FILE = '.noindex'

TMP_DIR = os.path.join(SERVER_ROOT, 'tmp')
