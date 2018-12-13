import logging
import time

from config import config

# Returns the date to be used in the HTTP response headers
def get_date():
    return time.strftime('%a, %d %B %Y %H:%M:%S', time.gmtime())

# Logging to log file: date, reques, status code and content length
def log_request(req, resp, f, to_screen=False, addr=None):
    # Log the request to the log file
    if not to_screen:
        with open(config.LOG_FILE, 'a') as log_file:
            log_file.write('[{}] {} "{}" {} {}\n'.format(get_date(), addr[0],
                            req.get_request(), resp.get_status_code(), f.get_content_length()))
    # Print the request to the screen
    else:
        print('[{}] "{}" {} {}'.format(get_date(), req.get_request(),
                resp.get_status_code(), f.get_content_length()))
