from OpenSSL import crypto
from os import path, environ
from ntpdatetime import NtpDatetime
from cryptography.exceptions import InvalidSignature
import cryptography.hazmat.primitives.asymmetric.padding as padding
import cryptography.hazmat.primitives.hashes as hashes
import urllib3
import requests

# Use a particular NTP server's time for cert verification in this module
datetime = NtpDatetime(environ.get('NTP_SERVER', 'time.nist.gov'))

# Accept SHA2 hashes.
# These and BLAKE2 are the secure hashes supported by the cryptography module
accepted_hashes = [
    hashes.SHA224,
    hashes.SHA256,
    hashes.SHA384,
    hashes.SHA512
]

def acceptable_hash(h):
    return any(isinstance(h, i) for i in accepted_hashes)

def load_cert(certpath):
    with open(certpath, 'rb') as cert:
        return crypto.load_certificate(crypto.FILETYPE_PEM, cert.read()).to_cryptography()

class VerificationError(ValueError):
    pass

# A simple (bad) certifcate verification function which checks that
# it is signed by one known CA, is valid for the current time,
# and uses a secure hashing algorithm
def verify_cert(peercert, cacert):
    hashalg = peercert.signature_hash_algorithm
    if not acceptable_hash(hashalg):
        raise VerificationError(
            "Unacceptable signature hashing algorithm {}"
            .format(hashalg.__class__.__name__)
        )

    try:
        cacert.public_key().verify(peercert.signature, peercert.tbs_certificate_bytes, padding.PKCS1v15(), hashalg)
    except InvalidSignature as e:
        raise VerificationError("Signature not valid") from e

    now = datetime.utcnow()
    if now > peercert.not_valid_after:
        raise VerificationError(
            "Certificate expired on {}".format(peercert.not_valid_after)
        )

    if now < peercert.not_valid_before:
        raise VerificationError(
            "Certificate not valid until {}".format(peercert.not_valid_before)
        )

class NaumHTTPAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs['cert_reqs'] = 'CERT_NONE'
        super().init_poolmanager(*args, **kwargs)

        # Patch the pool manager to use our custom connection pool
        # and by extension our custom connection
        # This is a (even more so than the rest of this code)
        # fragile way of achieving this
        self.poolmanager.pool_classes_by_scheme['https'] = NaumHTTPSConnectionPool

    def cert_verify(self, conn, url, verify, cert):
        if not path.isfile(verify):
            raise ValueError("verify must be set to a path to the single CA cert file")

        conn.ca_certs = verify

        # Disable OpenSSL certificate verification so we can do our own
        conn.cert_reqs = 'CERT_NONE'

class NaumHTTPSConnection(urllib3.connection.HTTPSConnection):
    def connect(self):
        self.cert_reqs = 'CERT_NONE'
        super().connect()

        # At this point in the execution we have an open connection,
        # who's certs have not been verified, but we have not yet
        # sent any applicaiton data
        # Here we will apply our own verification and raise and error
        # if our verification fails
        chain = self.sock.connection.get_peer_cert_chain()
        chain = [cert.to_cryptography() for cert in chain]
        verify_cert(chain[0], load_cert(self.ca_certs))

class NaumHTTPSConnectionPool(urllib3.connectionpool.HTTPSConnectionPool):
    ConnectionCls = NaumHTTPSConnection

# Example:
#    sess = requests.Session()
#    sess.verify = 'digicert.crt'
#    sess.mount("https://", NaumHTTPAdapter())
#    sess.get("https://mozilla.org")
