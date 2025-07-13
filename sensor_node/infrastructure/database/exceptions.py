class RecordNotFoundError(Exception):
    """Exception raised when a record is not found in the database."""

    def __init__(self, message="Record not found in the database."):
        self.message = message
        super().__init__(self.message)
