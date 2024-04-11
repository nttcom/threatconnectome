from httpx import Response


class HTTPError(Exception):
    code: int
    reason: str
    detail: str

    def __init__(self, response: Response):
        super().__init__()
        self.code = response.status_code
        self.reason = response.reason_phrase
        try:
            self.detail = response.json().get("detail", "")
        except Exception:
            self.detail = ""

    def __str__(self) -> str:
        return f"{self.code}: {self.reason}: {self.detail}"

    @classmethod
    def raise_from_response(cls, response: Response):
        raise HTTPError(response)
