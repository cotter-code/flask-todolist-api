import requests
import os 
import json
import jwt
from jwcrypto import jwk

CotterJWKSURL = "https://www.cotter.app/api/v0/token/jwks"

# ================ IMPORTANT ==================
# This validation example is for 
# TOOLS THAT ACCEPTS ANY API KEY ID
# For most users, you should use the validation functions
# that are available through the Cotter SDK
# to ensure that you ONLY accept JWT token that are
# generated for your API KEY ID.
# https://github.com/cotterapp/python-sdk#validating-tokens

def validate_access_token(access_token):
  # Getting jwt key
  r = requests.get(url = CotterJWKSURL);
  data = r.json();
  public_key_json = data["keys"][0];
  public_key_jwk = jwk.JWK.from_json(json.dumps(public_key_json))
  public_key = public_key_jwk.export_to_pem()

  # Getting access token and validate it
  access_token_resp = jwt.decode(access_token, key=public_key, algorithms=['ES256'], options={"verify_aud": False})

  return access_token_resp
  
def validate_id_token(id_token):
  # Getting jwt key
  r = requests.get(url = CotterJWKSURL);
  data = r.json();
  public_key_json = data["keys"][0];
  public_key_jwk = jwk.JWK.from_json(json.dumps(public_key_json))
  public_key = public_key_jwk.export_to_pem()

  id_token_resp = jwt.decode(id_token, key=public_key, algorithms=['ES256'], options={"verify_aud": False})

  return id_token_resp