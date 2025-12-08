import os

from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str = Header(...)):
    """
    API key (X-API-Key) is required for modifying vulns.

    Raises:
        HTTPException: If the API key is invalid, returns 401 Unauthorized.
    """
    if x_api_key != os.getenv("VULN_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API Key")
