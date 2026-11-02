import pytest

from app.sbom.pq_attestation import (
    ISSUER,
    generate_private_key,
    sign_sbom,
    verify_sbom,
)

SBOM = (
    b'{"bomFormat":"CycloneDX","specVersion":"1.5",'
    b'"components":[{"name":"openssl","version":"3.0.0"}]}'
)


@pytest.mark.parametrize("algorithm", ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"])
def test_sign_and_verify_round_trip(algorithm: str) -> None:
    private_key = generate_private_key(algorithm)
    public_key_raw = private_key.public_key().public_bytes_raw()

    attestation = sign_sbom(SBOM, algorithm=algorithm, private_key=private_key)
    assert attestation["issuer"] == ISSUER
    assert attestation["algorithm"] == algorithm

    assert verify_sbom(attestation, SBOM).valid
    assert verify_sbom(attestation, SBOM, expected_public_key=public_key_raw).valid


def test_detects_tampered_sbom() -> None:
    attestation = sign_sbom(SBOM)
    tampered = SBOM.replace(b"3.0.0", b"3.0.1")

    result = verify_sbom(attestation, tampered)
    assert not result.valid


def test_rejects_wrong_signer() -> None:
    attestation = sign_sbom(SBOM)
    other_public_key = generate_private_key().public_key().public_bytes_raw()

    result = verify_sbom(attestation, SBOM, expected_public_key=other_public_key)
    assert not result.valid


def test_rejects_unknown_algorithm() -> None:
    with pytest.raises(ValueError, match="Unsupported attestation algorithm"):
        sign_sbom(SBOM, algorithm="ML-DSA-99")
