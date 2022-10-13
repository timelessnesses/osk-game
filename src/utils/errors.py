class APIError(Exception):
    def __init__(self, error: str,*args: object) -> None:
        super().__init__(*args)
        self.error = error