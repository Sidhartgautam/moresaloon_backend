from dataclasses import dataclass

from rest_framework.response import Response


RESPONSE_STANDARD = {
    "success": True,
    "message": "",
    "data": {},
    "errors": [],
    "meta": {},
}


@dataclass
class PrepareResponse:
    """Improve Response Structure for the API."""

    success: bool = False
    message: str = ""
    data: dict or list = None
    errors: dict or list = None
    meta: dict = None

    def __init__(self, **kwargs):
        self.success = kwargs.get("success", False)
        self.message = kwargs.get("message", "")
        self.data = kwargs.get("data", {})
        self.errors = kwargs.get("errors", {})
        self.meta = kwargs.get("meta", {})

    @staticmethod
    def _format_response(**kwargs):
        """
        It takes a dictionary of keyword arguments and returns a copy of the
        RESPONSE_STANDARD dictionary with the keyword arguments added to it
        :return: A dictionary with the keys and values of the RESPONSE_STANDARD
        dictionary, plus the keys and values of the kwargs dictionary.
        """
        response = RESPONSE_STANDARD.copy()
        response.update(kwargs)
        return response

    def _to_json(self):
        return self._format_response(
            success=self.success,
            message=self.message,
            data=self.data,
            errors=self.errors,
            meta=self.meta,
        )

    def send(self, code=200):
        return Response(self._to_json(), status=code)


def exception_response(exception, serializer=None):
    data = serializer.data if hasattr(serializer, "data") else {}
    response = PrepareResponse(
        success=False,
        message=f"{exception.__class__.__name__} - {exception}",
        data=data,
    )
    return response.send(code=400)


__all__ = [
    "PrepareResponse",
    "exception_response",
]