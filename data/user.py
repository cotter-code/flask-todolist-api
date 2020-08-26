import os
from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient

FaunaDBSecret = os.getenv('FAUNA_DB_SECRET')
client = FaunaClient(secret=FaunaDBSecret)

def register(email, cotter_user_id):
  resp = client.query(
    q.create(
      q.collection("users"),
      {"data": {"email": email, "cotter_user_id": cotter_user_id}}
    )) 
  return resp

def get(cotter_user_id):
  resp = client.query(
              q.get(
                q.match(
                  q.index("user_by_cotter_user_id"),
                  cotter_user_id
                )
              ))
  return resp