import os
from faunadb import query as q
from faunadb.client import FaunaClient
from slugify import slugify

FaunaDBSecret = os.getenv('FAUNA_DB_SECRET')
client = FaunaClient(secret=FaunaDBSecret)

def create_list(cotter_user_id, name):
  tag = slugify(name)
  resp = client.query(
    q.create(
      q.collection("lists"),
      {"data": {"cotter_user_id": cotter_user_id, "name": name, "tag": tag}}
    )) 
  resp["id"] = resp["ref"].id()
  del resp["ref"]
  return resp

def get_lists_by_user(cotter_user_id):
  data = client.query(
              q.paginate(
                q.match(
                  q.index("lists_by_user"),
                  cotter_user_id
                )
              ))
  newData = []
  for d in data["data"]:
    resp = client.query(q.get(d))
    resp["id"] = resp["ref"].id()
    del resp["ref"]
    newData = newData + [resp]
  return newData

def get_list_by_user_and_tag(cotter_user_id, tag):
  resp = client.query(
              q.get(
                q.match(
                  q.index("list_by_user_and_tag"),
                  cotter_user_id,
                  tag
                )
              ))
  resp["id"] = resp["ref"].id()
  del resp["ref"]
  return resp

def update_list(list_id, name):
  tag = slugify(name)
  resp = client.query(
  q.update(
    q.ref(q.collection("lists"), list_id),
    {"data": {"name": name, "tag": tag}}
  ))
  resp["id"] = resp["ref"].id()
  del resp["ref"]
  return resp

def delete_list(list_id):
  resp = client.query(q.delete(q.ref(q.collection("lists"), list_id)))
  resp["id"] = resp["ref"].id()
  del resp["ref"]
  return resp

def create_todo(cotter_user_id, list_name, task):
  tag = slugify(list_name)
  lst = get_list_by_user_and_tag(cotter_user_id, tag)
  resp = client.query(
    q.create(
      q.collection("todos"),
      {"data": {"list_id": lst["id"], "task": task, "done": False}}
    ))
  resp["id"] = resp["ref"].id()
  del resp["ref"]
  return resp


def get_todos_by_list(list_id):
  data = client.query(
              q.paginate(
                q.match(
                  q.index("todo_by_list"),
                  list_id
                )
              ))
  newData = []
  for d in data["data"]:
    resp = client.query(q.get(d))
    resp["id"] = resp["ref"].id()
    del resp["ref"]
    newData = newData + [resp]
  return newData

def update_todo_done(task_id, done):
  resp = client.query(
  q.update(
    q.ref(q.collection("todos"), task_id),
    {"data": {"done": done}}
  ))
  resp["id"] = resp["ref"].id()
  del resp["ref"]
  return resp

def update_todo_task(task_id, task):
  resp = client.query(
  q.update(
    q.ref(q.collection("todos"), task_id),
    {"data": {"task": task}}
  ))
  resp["id"] = resp["ref"].id()
  del resp["ref"]
  return resp

def delete_todo(task_id):
  resp = client.query(q.delete(q.ref(q.collection("todos"), task_id)))
  resp["id"] = resp["ref"].id()
  del resp["ref"]
  return resp

def get_todo_list_by_user(cotter_user_id):
  lists = get_lists_by_user(cotter_user_id)
  newLists = []
  for lst in lists:
    print(lst)
    todos = get_todos_by_list(lst["id"])
    newLst = lst
    newLst["todos"] = todos
    newLists = newLists + [newLst]
  
  return newLists

def get_todo_list_by_user_and_tag(cotter_user_id, tag):
  lst = get_list_by_user_and_tag(cotter_user_id, tag)
  todos = get_todos_by_list(lst["id"])
  lst["todos"] = todos
  return lst