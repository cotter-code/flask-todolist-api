import os
import json
from functools import wraps
from flask import g
from flask import Flask, abort
from flask import request
from flask_cors import CORS
from auth import validate_access_token, validate_id_token
import faunadb
from data import user, todolist

# Constants

app = Flask(__name__)
CORS(app)


# Middleware for login
def login_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    # Check if auth_header exists
    auth_header = request.headers.get('Authorization')
    if auth_header:
      access_token = auth_header.split(" ")[1]
    else:
      abort(401, 'Authorization header is missing')
    
    # Validate JWT token
    try:
      print(access_token)
      access_token_resp = validate_access_token(access_token)
      g.access_token = access_token_resp
    except:
      abort(401, "Invalid oauth tokens")
      
    return f(*args, **kwargs)
  return decorated_function


@app.route('/')
def index():
    return '<h1>Welcome to <a href="https://www.cotter.app">Cotter\'s</a> To-do List API</h1>'

# Registration and Login endpoint
@app.route('/login_register', methods=['POST'])
def login_register():
    req = request.get_json();

    # Validate JWT token
    try:
      access_token_resp = validate_access_token(req["oauth_token"]["access_token"])
      id_token_resp = validate_id_token(req["oauth_token"]["id_token"])
    except:
      abort(401, "Invalid oauth tokens")
    
    # Register or Login the user
    try:
      # Register the user
      resp = user.register(id_token_resp["identifier"], access_token_resp["sub"])
      user_id = resp["ref"].id()
    except faunadb.errors.BadRequest as err:
      if "not unique" in str(err):
        try:
          # If user exists, get user from database (logging-in)
          resp = user.get(access_token_resp["sub"])
          user_id = resp["ref"].id()
        except faunadb.errors.BadRequest as err:
          abort(500, 'Something went wrong when getting the user: ' + str(err))
      else:
        abort(500, 'Something went wrong when registering the user: ' + str(err))

    # Return the user
    user_data = {
      "user_id": user_id
    }
    return user_data

# LISTS FUNCTIONS
# Create a new todo list
@app.route('/list/create', methods=['POST'])
@login_required
def create_list():
    if g.access_token is None:
      abort(401, 'Access token is missing')

    req = request.get_json();
    try:
      resp = todolist.create_list(g.access_token["sub"], req["name"])
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when creating a new list: ' + str(err))

    return json.dumps(resp)

# List all todo lists
@app.route('/list', methods=['GET'])
@login_required
def get_lists():
    if g.access_token is None:
      abort(401, 'Access token is missing')

    try:
      resp = todolist.get_todo_list_by_user(g.access_token["sub"])
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when getting lists: ' + str(err))

    return json.dumps(resp)

# List by list name
@app.route('/list/<tag>', methods=['GET'])
@login_required
def get_list_by_name(tag):
    if g.access_token is None:
      abort(401, 'Access token is missing')

    try:
      resp = todolist.get_todo_list_by_user_and_tag(g.access_token["sub"], tag)
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when getting list by name: ' + str(err))

    return json.dumps(resp)


# Update list by id
@app.route('/list/update/<list_id>', methods=['PUT'])
@login_required
def update_list(list_id):
    if g.access_token is None:
      abort(401, 'Access token is missing')

    req = request.get_json();
    try:
      resp = todolist.update_list(list_id, req["name"])
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when getting list by name: ' + str(err))

    return json.dumps(resp)

# Delete list by id
@app.route('/list/delete/<list_id>', methods=['DELETE'])
@login_required
def delete_list(list_id):
    if g.access_token is None:
      abort(401, 'Access token is missing')

    req = request.get_json();
    try:
      resp = todolist.delete_list(list_id)
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when getting list by name: ' + str(err))

    return json.dumps(resp)



# TODOS FUNCTIONS
# Add items to the todo list
@app.route('/todo/create', methods=['POST'])
@login_required
def add_todo_to_list():
    if g.access_token is None:
      abort(401, 'Access token is missing')

    req = request.get_json();
    try:
      resp = todolist.create_todo(g.access_token["sub"], req["name"], req["task"])
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when creating a new todo: ' + str(err))

    return json.dumps(resp)


# Update item in the todo list done or not
# {"done": boolean}
@app.route('/todo/update/done/<task_id>', methods=['PUT'])
@login_required
def update_todo_done(task_id):
    if g.access_token is None:
      abort(401, 'Access token is missing')

    req = request.get_json();
    try:
      resp = todolist.update_todo_done(task_id, req["done"])
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when updating todo: ' + str(err))

    return json.dumps(resp)

# Update item task in the todo list
# {"task": string}
@app.route('/todo/update/task/<task_id>', methods=['PUT'])
@login_required
def update_todo_task(task_id):
    if g.access_token is None:
      abort(401, 'Access token is missing')

    req = request.get_json();
    try:
      resp = todolist.update_todo_task(task_id, req["task"])
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when updating todo: ' + str(err))

    return json.dumps(resp)

# Delete todo
@app.route('/todo/delete/<task_id>', methods=['DELETE'])
@login_required
def delete_todo(task_id):
    if g.access_token is None:
      abort(401, 'Access token is missing')

    req = request.get_json();
    try:
      resp = todolist.delete_todo(task_id)
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when deleting todo: ' + str(err))

    return json.dumps(resp)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=1234)