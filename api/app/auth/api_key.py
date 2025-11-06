import os

from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str = Header(...)):
    """
    API key (X-API-Key) is required for modifying vulns and actions.

    Raises:
        HTTPException: If the API key is invalid, returns 403 Forbidden.
    """
    if x_api_key != os.getenv("VULN_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API Key")
