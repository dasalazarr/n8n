class Response:
    def __init__(self, status_code=503, text=''):
        self.status_code = status_code
        self.text = text
    def json(self):
        return {}

def post(*args, **kwargs):
    """Minimal stub returning empty response."""
    return Response()
