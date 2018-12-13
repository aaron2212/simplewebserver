import gzip
import magic
import os
import time

from config import config
from core.exceptions import HTTP404Error
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class File():
    def __init__(self, full_path=None):
        # full_path stores the entire path to the file; request_path stores the path from the request
        self.full_path = full_path
        self.mode = 'r'
        self.content_length = None
        self.requested_path = None

        # Allows for compression of the file before being sent, if the browser supports it
        self.compression_method = None

        # Information about the file to be used with directory listing
        self.filename = None
        self.filesize = None
        self.last_modified_time = None
        self.description = None

    def get_file_contents(self):
        # Get the file contents to be sent back with the HTTP Response
        self.mode = 'rb' if self.is_binary() else 'r'

        fo = open(self.full_path, self.mode)
        file_contents = fo.read()

        # If compression is not supported by the browser, send back the uncompressed contents
        if self.compression_method is not None:
            file_contents = self.compress_contents(file_contents)
            self.content_length = len(file_contents)
        else:
            self.content_length = len(file_contents)

        self.set_content_length(self.content_length)

        return file_contents, self.content_length

    def compress_contents(self, file_contents):
        # If the browser supports gzip compression, compress the file using gzip
        if self.compression_method == 'gzip':
            f = os.path.join(config.TMP_DIR, self.get_filename())
            # Convert the file contents to bytes if it is not already bytes
            file_contents = file_contents.encode('utf-8') if (
                type(file_contents) == str) else file_contents

            # Compress the file contents and write it to a temporary file
            gz_file = gzip.GzipFile(filename=f, mode='wb')
            gz_file.write(file_contents)
            gz_file.close()

            # Read the compressed file contents
            compressed_file = open(f, 'rb')
            compressed_contents = compressed_file.read()

            self.content_length = len(compressed_contents)
            gz_file.close()

            # Delete the temporary file
            os.unlink(f)

        return compressed_contents

    def render_template(self, template_name):
        # Get the template to be rendered
        file_loader = FileSystemLoader(config.PATH_TO_TEMPLATES)

        env = Environment(loader=file_loader)
        template = env.get_template(template_name)

        url = self.requested_path[:-1] if self.requested_path.endswith('/') else self.requested_path
        listing_path = os.path.join(config.FILES_DIR, self.requested_path[1:])

        files = []

        # If the template to be rendered is for directory listing, generate a list of files
        if template_name == 'listing.html':
            for file_ in os.listdir(listing_path):
                filename = file_
                path = os.path.join(listing_path, filename)

                # Check whether the directory contains a .noindex file and do not list it if it does
                if os.path.isdir(path) and config.NOINDEX_FILE not in os.listdir(path) or os.path.isfile(path):
                    # Check if the file is a directory. If it is, set the size to '-'
                    is_dir = os.path.isdir(os.path.join(listing_path, filename))

                    filesize = os.path.getsize(os.path.join(listing_path, filename)) if not is_dir else '-'
                    last_modified_time = os.path.getmtime(os.path.join(listing_path, filename))

                    f = File(self.full_path)

                    # Set the file information to be displayed in the directory listing template
                    f.set_filename(filename)
                    f.set_filesize(filesize)
                    f.set_last_modified_time(last_modified_time)

                    files.append(f)

        # Set the parameters to used in the template
        file_contents = template.render(url=url, server_name=config.SERVER_NAME,
                                        host=config.HOST, port=config.PORT, files=files)

        if self.compression_method is not None:
            file_contents = self.compress_contents(file_contents)
            content_length = len(file_contents)
        else:
            content_length = len(file_contents)

        # Set the file content's length to be used in the Content-Length HTTP header
        self.set_content_length(content_length)

        return file_contents, content_length

    def set_filename(self, filename):
        self.filename = filename

    def set_filesize(self, filesize):
        # Get the size of the file in human readable form, showing B, KB, MB or GB

        # Get the size of the file if it is not a directory
        if filesize != '-':
            if filesize < 1024:
                self.filesize = str(filesize) + 'B'
            elif filesize >= 1024 and filesize < (1024**2):
                self.filesize = str(round((filesize/1024), 2)) + 'KB' # MB
            elif filesize >= (1024**2) and filesize < (1024**3):
                self.filesize = str(round(filesize/(1024**2), 2)) + 'MB' # GB
            elif filesize >= (1024**3) and filesize < (1024**4):
                self.filesize = str(round(filesize/(1024**3), 2)) + 'GB'
        else:
            self.filesize = '-'

    def set_last_modified_time(self, last_modified_time):
        # Show the last modified time of the file in a nice date format
        last_modified_time = datetime.fromtimestamp(last_modified_time)
        self.last_modified_time = datetime.strftime(last_modified_time,
                                    '%Y-%m-%d %H:%M')

    def get_mime_type(self):
        # Get the MIME type of the file to be used to check if the file is a binary and to set the Content-Type HTTP header
        TEXT_MIME_TYPES = {
            'html': 'text/html',
            'css': 'text/css',
            'js': 'text/javascript'
        }
        mime = magic.Magic(mime=True)

        if mime.from_file(self.full_path).startswith('text/'):
            ext = os.path.splitext(self.full_path)[1][1:]
            return TEXT_MIME_TYPES[ext]
        else:
            return mime.from_file(self.full_path)

    def is_binary(self):
        # Return true if the file is a binary file
        # If the MIME type starts with 'text/', then it is not a binary file
        return False if self.get_mime_type().startswith('text/') else True

    def get_filename(self):
        return os.path.split(self.full_path)[1]

    def get_path_info(self):
        # Checks whether the path exists and if it is a directory or a file
        if os.path.exists(self.full_path):
            if os.path.isdir(self.full_path):
                return 'directory'
            elif os.path.isfile(self.full_path):
                return 'file'
        # Path does not, raise HTTP404Error
        else:
            raise HTTP404Error

    def is_path_listable(self):
        # Checks whether directory listing is enabled
        # Also check for presence of '.noindex' file
        path = os.path.join(self.full_path, config.NOINDEX_FILE)

        if config.DIRECTORY_LISTING_ENABLED and not os.path.exists(path):
            return True
        else:
            return False

    def set_full_path(self, full_path):
        # Sets the full path to the file to be sent in the response
        self.full_path = full_path

    def set_requested_path(self, requested_path):
        self.requested_path = requested_path

    def set_path_listing(self, path_listing):
        self.path_listing = path_listing

    def get_content_length(self):
        return self.content_length

    def set_content_length(self, content_length):
        self.content_length = content_length

    def set_compression_method(self, compression_method):
        self.compression_method = compression_method

    def get_compression_method(self):
        return self.compression_method

    def get_index_file(self):
        # Retrieves the index file when the user requested '/' as the path
        web_files = os.listdir(config.FILES_DIR)

        # Search the directory for index files (defined by FILES_DIR)
        if len(web_files) > 0:
            for i, f in enumerate(web_files):
                if f in config.INDEX_FILES:
                    return f
                else:
                    if i == len(web_files)-1:
                        raise HTTP404Error
        # No index file found
        else:
            raise HTTP404Error

    def generate_404(self):
        self.full_path = config.PATH_TO_404

        return self.render_template('404.html')
