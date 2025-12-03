class UnifiedValidationException(Exception):
    def __init__(self, validation_errors: list, status_code: int = 422):
        self.validation_errors = validation_errors
        self.status_code = status_code
        super().__init__("Validation error")
