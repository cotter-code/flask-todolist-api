# Cotter Todo List Backend with Flask

This is an example to show how to build a backend REST API in Flask using [Cotter](https://www.cotter.app) for Authorization.

Tech stack used:
- Flask
- JWT Authentication using [Cotter's OAuth Tokens](https://docs.cotter.app/getting-access-token/handling-authentication-with-cotter)
- FaunaDB for serverless database

# API
The API is available at https://cottertodolist.herokuapp.com. API Reference is available at `api.http`

# Basic Concepts
The easiest way to protect your API routes to always require a valid access token is by creating a middleware. You can then use this middleware in protected routes easily.

## Creating a Middleware

Make a middleware called `login_required`:
```python
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
      access_token_resp = validate_access_token(access_token) # 👈 see auth.py
      g.access_token = access_token_resp
    except:
      abort(401, "Invalid oauth tokens")
      
    return f(*args, **kwargs)
  return decorated_function
```
Find the function definition for `validate_access_token` and `validate_id_token` in `auth.py`.

## Using the Middleware
On the API routes that requirest login, do the following:
```python
# LISTS FUNCTIONS
# Create a new todo list
@app.route('/list/create', methods=['POST'])
@login_required  # 👈 Call our middleware before continuing with the request
def create_list():
    if g.access_token is None:
      abort(401, 'Access token is missing')

    req = request.get_json();
    try:
      resp = todolist.create_list(g.access_token["sub"], req["name"])
    except faunadb.errors.BadRequest as err:
        abort(500, 'Something went wrong when creating a new list: ' + str(err))

    return json.dumps(resp)
```

# Deploying
### Required Environment Variables:
```
export FAUNA_DB_SECRET=<Your Fauna DB Secret>
export COTTER_API_KEY_ID=<Your API KEY ID>
```
- `COTTER_API_KEY_ID`: Obtain one from [Cotter's Dashboard](https://dev.cotter.app/)
- `FAUNA_DB_SECRET`: Obtain one from [FaunaDB](https://fauna.com/)

### DB Schema in FaunaDB

Database Name: todolist

Collections:
- lists
- todos
- users

Indexes:
- list_by_user_and_tag
- list_unique_tag
- lists_by_user
- todo_by_list
- unique_cotter_user_id
- unique_email
- user_by_cotter_user_id
- user_by_email
