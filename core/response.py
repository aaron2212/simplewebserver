from config import config

class Response():
    def __init__(self, client, status_code):
        # Response to be sent back to the client
        self.client = client
        self.status_code = status_code
        self.response_headers = config.STANDARD_RESPONSE_HEADERS
        self.data = None
        self.resp_str = None

        self.status_codes = {
            200: 'OK',
            400: 'Bad Request',
            404: 'Not Found',
            405: 'Method Not Allowed'
        }

    def get_status_code(self):
        # Get the response status code
        return self.status_code

    def add_header(self, header, value):
        # Add an HTTP header onto the default STANDARD_RESPONSE_HEADER set in config.py
        self.response_headers[header] = value

    def remove_header(self, header):
        self.response_headers.pop(header, None)

    def add_data(self, data):
        # Add data to be sent along with the HTTP response
        self.data = data

    def send(self):
        # Create a response
        self.resp_str = 'HTTP/1.1 {} {}\r\n'.format(self.status_code, self.status_codes[self.status_code])

        # Add the response headers
        for header in self.response_headers:
            self.resp_str += '{}: {}\r\n'.format(header, self.response_headers[header])

        # Add extra line; data follows or end of response
        self.resp_str += '\r\n'

        # Add data (file contents) to response
        self.client.send(self.resp_str.encode('utf-8'))

        if type(self.data) == str:
            self.client.send(self.data.encode('utf-8'))
        else:
            self.client.send(self.data)
