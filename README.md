# FileShareAPI Flask Wrapper

This repository contains a mock file-sharing backend (`file_sharing_api.py`) and a small Flask wrapper (`server.py`) that exposes REST endpoints for interacting with the mock API.

**Quick summary**: `server.py` exposes endpoints for creating users and files, sharing files, reading/updating/deleting files (authorization enforced by the mock API), listing files (debug), and resetting state.

**Important**: The mock API intentionally contains authorization bugs for testing. See `file_sharing_api.py` comments. The Flask wrapper forwards those behaviors unchanged unless you ask me to patch them.

**Prerequisites**

- Python 3.8+ installed
- (Recommended) Use a virtual environment

**Install & run (PowerShell)**

```powershell
# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

The server listens on `http://0.0.0.0:5000` by default (accessible at `http://localhost:5000`).

**Endpoints**

- `GET /` — Health/info
- `POST /users` — Create user
  - JSON: `{ "email": "...", "organization_id": "...", "name": "..." }`
- `GET /users/<user_id>` — Get user info
- `POST /files` — Create file
  - JSON: `{ "owner_id": "...", "name": "...", "visibility": "private|shared|org_public|public", "content": "..." }`
- `GET /files/<file_id>?user_id=<user_id>` — Read file (requires `user_id` query param)
- `PUT /files/<file_id>` — Update file
  - JSON: `{ "user_id": "...", "content": "..." }`
- `DELETE /files/<file_id>?user_id=<user_id>` — Delete file (requires `user_id` query param)
- `POST /files/<file_id>/share` — Share file
  - JSON: `{ "user_id": "...", "target_user_id": "...", "permission_type": "read|edit" }`
- `GET /files/<file_id>/permissions?user_id=<user_id>` — Get file permissions (owner-only)
- `GET /files` — Debug: list all files
- `POST /reset` — Reset API state (clears users, files, permissions)

**Example requests**

PowerShell (native):

```powershell
# Create a user
$body = @{ email = 'alice@acme.com'; organization_id = 'org-acme'; name = 'Alice' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/users -Body $body -ContentType 'application/json'

# Create a file (use returned user_id)
$body = @{ owner_id = '<user_id>'; name = 'private.txt'; visibility = 'private'; content = 'Secret' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/files -Body $body -ContentType 'application/json'

# Read a file (replace placeholders)
Invoke-RestMethod -Method Get -Uri "http://localhost:5000/files/<file_id>?user_id=<user_id>"

# Share a file
$body = @{ user_id = '<owner_id>'; target_user_id = '<other_user_id>'; permission_type = 'read' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:5000/files/<file_id>/share -Body $body -ContentType 'application/json'

# Reset API state
Invoke-RestMethod -Method Post -Uri http://localhost:5000/reset
```

cURL (POSIX / Git Bash):

```bash
# Create a user
curl -s -X POST http://localhost:5000/users \
  -H 'Content-Type: application/json' \
  -d '{"email":"alice@acme.com","organization_id":"org-acme","name":"Alice"}'

# Read file
curl -s "http://localhost:5000/files/<file_id>?user_id=<user_id>"
```

**Notes & recommendations**

- The mock API includes intentional authorization bugs (documented in `file_sharing_api.py`). If you plan to use this server for demos or integration tests where correct authorization is required, I can:
  - Patch `file_sharing_api.py` to fix the logic, or
  - Add request-level checks in `server.py` to override the buggy behavior.

- `GET /files` is a debug endpoint that returns all files and may expose data you don't want in production. Remove or secure it for production use.

- To add CORS for browser access, install `flask-cors` and configure it in `server.py`.

---

If you'd like, I can now:

- Fix the intentional authorization bugs in `file_sharing_api.py` and add tests, or
- Add a small Postman collection / OpenAPI spec for the Flask wrapper.

Tell me which next step you prefer.

**Testing the API (HTTP-based tests)**

Follow these steps to run the Flask server and execute the HTTP-based test suite (`test_framework.py`). The server must be running before starting the tests.

1) Prepare environment

```powershell
# From the project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Start the Flask server (keep this shell open)

Option A — run directly:
```powershell
# start server in current shell
python server.py
```

Option B — use `flask run`:
```powershell
$env:FLASK_APP = 'server:app'
$env:FLASK_ENV = 'development'   # optional, enables auto-reload
flask run --host=0.0.0.0 --port=5000 --reload
```

3) Sanity check (optional — new shell)

```powershell
.\.venv\Scripts\Activate.ps1
Invoke-RestMethod -Method Get -Uri http://localhost:5000/
```

4) Run the tests (new shell)

```powershell
.\.venv\Scripts\Activate.ps1
python test_framework.py
```

What to expect
- The test runner will create users and files via the HTTP API, run all policy scenarios, print progress and a summary, and write `test_results.json` in the project root.

Troubleshooting
- If you see "Connection refused", ensure the server is running at `http://localhost:5000` and that you started it from the same environment where dependencies are installed.
- If `requests` is missing, re-run `pip install -r requirements.txt` in the virtualenv.
- If port 5000 is in use, change the port in `server.py` or pass a different `--port` to `flask run`, and update `ApiClient(base_url=...)` in `test_framework.py` accordingly.

Automation option
- If you want, I can add a `run.ps1` script that starts the server (background) and runs the tests automatically. Ask and I will create it.