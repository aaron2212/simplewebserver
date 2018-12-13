from config import config

class Request():
    def __init__(self, data):
        # Create a request from the data received
        self.data = data

        self.request = self.data.split('\r\n')[0].split()
        self.request_headers = self.data.split('\r\n')[1:][:-2]

        self.headers = {}

        for header in self.request_headers:
            key = header.split(':')[0]
            value = header.split(':')[1].lstrip()

            self.headers[key] = value

    def validate(self):
        # Validate the request and return the status code

        # Return 400 Bad Request for malformed HTTP request
        if len(self.request) != 3:
            return 400
        # Return 405 Method Not Allowed for unsupported HTTTP method
        elif self.get_request_method() not in config.HTTP_METHODS:
            return 405
        # Return 200 OK if HTTP request was valid
        else:
            return 200

    def get_request(self):
        return '{} {} {}'.format(self.get_request_method(), self.get_path(), self.get_version())

    def get_request_method(self):
        # Return the method used in the request
        return self.request[0]

    def get_path(self):
        # Returns the path from the request
        return self.request[1]

    def get_version(self):
        # Returns the HTTP version used in the request
        return self.request[2]

    def has_header(self, header):
        return True if header in self.headers else False

    def get_header(self, header):
        return self.headers.get(header, None)
