class InvestigationError(Exception):
    """An expected failure with a safe, user-facing explanation."""

    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason
        self.message = message
