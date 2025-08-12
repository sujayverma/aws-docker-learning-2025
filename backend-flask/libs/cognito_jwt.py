import json
import requests
from jose import jwk, jwt
from jose.utils import base64url_decode
from flask import request
import os
import time

REGION = os.getenv('AWS_REGION')
USER_POOL_ID = os.getenv('REACT_APP_AWS_USER_POOLS_ID')
CLIENT_ID = os.getenv('REACT_APP_CLIENT_ID')

JWKS_URL = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

jwks = requests.get(JWKS_URL).json()["keys"]

class CognitoJwt:

    def __init__(self, bearer):
        self.token = self.get_token(bearer)

    def get_token(self, bearer):
        return bearer.split(" ")[1]

    def verify_cognito_token(self):
        headers = jwt.get_unverified_headers(self.token)
        kid = headers["kid"]

        # Find the JWK that matches the kid
        key_index = -1
        for i in range(len(jwks)):
            if kid == jwks[i]["kid"]:
                key_index = i
                break
        if key_index == -1:
            raise Exception("Public key not found in JWKs")

        # Construct the public key
        public_key = jwk.construct(jwks[key_index])

        # Get claims without verification (for expiry check)
        claims = jwt.get_unverified_claims(self.token)

        # Expiration check
        if claims["exp"] < int(time.time()):
            raise Exception("Token is expired")

        # Audience check
        if claims.get("aud") != CLIENT_ID:
            raise Exception("Token was not issued for this audience")

         # Verify the signature
        message, encoded_sig = str(token).rsplit(".", 1)
        decoded_sig = base64url_decode(encoded_sig.encode("utf-8"))

        if not public_key.verify(message.encode("utf-8"), decoded_sig):
            raise Exception("Signature verification failed")

        return claims  # ✅ valid token, return claims


