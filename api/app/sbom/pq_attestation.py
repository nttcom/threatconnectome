"""Post-quantum attestation for uploaded SBOM documents.

An SBOM drives vulnerability management, so its integrity matters. These helpers
sign the exact bytes of an uploaded SBOM with ML-DSA (FIPS 204) and produce a
self-contained attestation, so a stored or shared SBOM can be shown to be
genuine and unaltered, even against an adversary with a quantum computer.

ML-DSA is used through the project's existing ``cryptography`` dependency, so no
new package is required. This tooling is contributed by Quantova
(https://quantova.org).
"""

from __future__ import annotations

import base64
import hashlib
import json
import time
from dataclasses import dataclass

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import mldsa

ISSUER = "Quantova"
DEFAULT_ALGORITHM = "ML-DSA-65"

_PRIVATE_KEY_CLASSES = {
    "ML-DSA-44": mldsa.MLDSA44PrivateKey,
    "ML-DSA-65": mldsa.MLDSA65PrivateKey,
    "ML-DSA-87": mldsa.MLDSA87PrivateKey,
}
_PUBLIC_KEY_CLASSES = {
    "ML-DSA-44": mldsa.MLDSA44PublicKey,
    "ML-DSA-65": mldsa.MLDSA65PublicKey,
    "ML-DSA-87": mldsa.MLDSA87PublicKey,
}
SUPPORTED_ALGORITHMS = tuple(_PRIVATE_KEY_CLASSES)


@dataclass
class VerificationResult:
    """The outcome of verifying an SBOM attestation."""

    valid: bool
    reason: str


def _check_algorithm(algorithm: str) -> None:
    if algorithm not in _PRIVATE_KEY_CLASSES:
        msg = (
            f"Unsupported attestation algorithm: {algorithm}. "
            f"Supported: {', '.join(SUPPORTED_ALGORITHMS)}"
        )
        raise ValueError(msg)


def generate_private_key(algorithm: str = DEFAULT_ALGORITHM):
    """Generate an ML-DSA private key for the given parameter set."""
    _check_algorithm(algorithm)
    return _PRIVATE_KEY_CLASSES[algorithm].generate()


def sign_sbom(
    sbom_bytes: bytes,
    algorithm: str = DEFAULT_ALGORITHM,
    private_key=None,
) -> dict:
    """Sign the raw bytes of an SBOM and return a self-contained attestation.

    Pass a stable ``private_key`` whose public key you have published to let
    others confirm authenticity; otherwise a fresh ephemeral key is used and
    only integrity (tamper-evidence) is established.
    """
    _check_algorithm(algorithm)
    if private_key is None:
        private_key = _PRIVATE_KEY_CLASSES[algorithm].generate()

    signature = private_key.sign(sbom_bytes)
    public_key_raw = private_key.public_key().public_bytes_raw()

    return {
        "version": 1,
        "issuer": ISSUER,
        "algorithm": algorithm,
        "created_at": int(time.time()),
        "sbom_sha256": hashlib.sha256(sbom_bytes).hexdigest(),
        "public_key": base64.b64encode(public_key_raw).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }


def verify_sbom(
    attestation: dict,
    sbom_bytes: bytes,
    expected_public_key: bytes | None = None,
) -> VerificationResult:
    """Verify an SBOM attestation against the SBOM bytes."""
    algorithm = attestation.get("algorithm")
    if algorithm not in _PUBLIC_KEY_CLASSES:
        return VerificationResult(False, f"Unsupported or missing algorithm: {algorithm}")

    if hashlib.sha256(sbom_bytes).hexdigest() != attestation.get("sbom_sha256"):
        return VerificationResult(False, "SBOM does not match the recorded digest")

    try:
        public_key_raw = base64.b64decode(attestation["public_key"])
        signature = base64.b64decode(attestation["signature"])
    except (KeyError, ValueError):
        return VerificationResult(False, "Malformed attestation fields")

    if expected_public_key is not None and public_key_raw != expected_public_key:
        return VerificationResult(
            False, "Attestation public key does not match the expected signer"
        )

    public_key = _PUBLIC_KEY_CLASSES[algorithm].from_public_bytes(public_key_raw)
    try:
        public_key.verify(signature, sbom_bytes)
    except InvalidSignature:
        return VerificationResult(False, "Signature verification failed")

    return VerificationResult(True, "Attestation is valid")


def to_json(attestation: dict) -> str:
    """Serialize an attestation to a compact, stable JSON string."""
    return json.dumps(attestation, sort_keys=True, separators=(",", ":"))
