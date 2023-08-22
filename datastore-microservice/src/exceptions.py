class MYSQLConnectionError(Exception):
    """ Failed to connect to mysql database """
    def __init__(self, host, port):
        super().__init__(f"Could not connect to mysql database on {host}:{port}")
        
class MissingTableError(Exception):
    def __init__(self, message):
        super().__init__(message)