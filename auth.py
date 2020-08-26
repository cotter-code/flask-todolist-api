import requests
import os 
from jose import jwt

CotterJWKSURL = "https://www.cotter.app/api/v0/token/jwks"
API_KEY_ID = os.getenv('COTTER_API_KEY_ID')


def validate_access_token(access_token):
  # Getting jwt key
  r = requests.get(url = CotterJWKSURL);
  data = r.json();
  public_key = data["keys"][0];

  # Getting access token and validate it
  access_token_resp = jwt.decode(access_token, public_key, algorithms='ES256', audience=API_KEY_ID)
  
  return access_token_resp
  
def validate_id_token(id_token):
  # Getting jwt key
  r = requests.get(url = CotterJWKSURL);
  data = r.json();
  public_key = data["keys"][0];

  id_token_resp = jwt.decode(id_token, public_key, algorithms='ES256', audience=API_KEY_ID)

  return id_token_resp