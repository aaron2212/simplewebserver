import importlib
import os
import socket
import threading

from config import config
from core import file, request, response
from core.exceptions import HTTP404Error
from misc import misc

# TODO: add documentation for methods and classes (and inline documentation)

class WebServer():
    def __init__(self, host, port):
        # Setup the web server
        self.host = host
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(config.CONNECTION_BACKLOG)

        print('Started web server on {}:{}'.format(self.host, self.port))
        print('Type q and press enter to quit the server...')

        # Continue to accept connections from clients and start a new thread to handle each connection
        while 1:
            try:
                client, addr = self.sock.accept()

                thread = threading.Thread(target=self.handle_connection, args=(client, addr))
                thread.daemon = True

                thread.start()
            except ConnectionResetError:
                pass

    def handle_connection(self, client, addr):
        data = client.recv(1024).decode('utf-8')

        # Filter out empty requests sent by the browser
        if data:
            req = request.Request(data)

            status_code = req.validate()

            # Stores the file's information to be sent back in the response
            file_contents = None
            content_length = None
            content_type = None

            # Holds information about the file to be sent in the response
            f = file.File()

            # HTTP request was OK
            if status_code == 200:
                path = req.get_path()
                f.set_requested_path(path)

                # Add support for gzip compression
                if req.has_header('Accept-Encoding'):
                    if 'gzip' in req.get_header('Accept-Encoding'):
                        f.set_compression_method('gzip')

                # Try to retrieve the requested file
                try:
                    # If the user requested the root directory, return the index file
                    if path == '/':
                        full_path = os.path.join(config.SERVER_ROOT, config.FILES_DIR)
                        # If there are files in the web files directory
                        index_file = f.get_index_file()
                        f.set_full_path(os.path.join(full_path, index_file))
                        file_contents, content_length = f.get_file_contents()
                    # User did not request an index file
                    else:
                        full_path = os.path.join(config.FILES_DIR, path[1:])

                        # Check if file exists, is a directory or a file
                        f.set_full_path(full_path)
                        path_info = f.get_path_info()
                        listing_template_path = os.path.join(config.SERVER_ROOT, config.PATH_TO_LISTING)

                        if path_info == 'directory':
                            # Check if directory listing is enabled
                            if f.is_path_listable():
                                f.set_full_path(listing_template_path)
                                file_contents, content_length = f.render_template('listing.html')
                            else:
                                raise HTTP404Error
                        elif path_info == 'file':
                            # Serve the file
                            file_contents, content_length = f.get_file_contents()
                except HTTP404Error:
                    # File not found, generate 404
                    status_code = 404
                    file_contents, content_length = f.generate_404()

            # Prepare response for sending
            resp = response.Response(client, status_code)

            # Log the request to the file, if logging is enabled
            if config.LOGGING_ENABLED:
                misc.log_request(req, resp, f, addr=addr)

            # Print the request to the screen
            misc.log_request(req, resp, f, to_screen=True)

            # If a file needs to be sent, set its Content-Type and Content-Length HTTP headers
            if file_contents is not None:
                # If the file is a binary file, tell the browser to download it
                if f.is_binary():
                    resp.add_header('Content-Type', 'application/octet-stream')
                    resp.add_header('Content-Disposition', 'attachment; filename=' + f.get_filename())
                else:
                    resp.remove_header('Content-Disposition')
                    resp.add_header('Content-Type', f.get_mime_type())

                # If the browser supports compression, add the 'Accept-Encoding' HTTP header
                if req.has_header('Accept-Encoding'):
                    if 'gzip' in req.get_header('Accept-Encoding'):
                        resp.add_header('Content-Encoding', 'gzip')
                else:
                    resp.remove_header('Content-Encoding')

                resp.add_header('Content-Length', content_length)

                resp.add_data(file_contents)

            resp.send()

            # Close the connection
            client.close()

def main():
    host = config.HOST
    port = config.PORT

    server = WebServer(host, port)

    server.start()

if __name__ == '__main__':
    main()
