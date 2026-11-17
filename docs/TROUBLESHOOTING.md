# Troubleshooting

## Setup and first run

1. Accept the lecturer's classroom50 assignment and open **your** repository in a GitHub Codespace. Wait for the container setup to finish. It creates the root `.venv` and installs the pinned dependencies.
2. In VS Code's Explorer, right-click **this exercise's folder** and choose **Open in Integrated Terminal**. This avoids accidentally running a different `app.py`.
3. Check the interpreter and install the local dependency list if setup was interrupted:

   ```bash
   python --version
   python -m pip install -r requirements.txt
   ```

   The version must begin `Python 3.14`. If it does not, rebuild the supplied container and select the repository's `.venv/bin/python` interpreter. Do not silently continue on a different Python version.
4. Run the browser application:

   ```bash
   python app.py
   ```

5. Open the forwarded port **5000** from the Ports panel. Confirm its visibility is **Private**. Sign in using the account table below. The browser URL ends with `.app.github.dev` in Codespaces.
6. Use a second terminal in this same exercise folder for tests and API examples. Stop the server with **Ctrl+C** before changing exercises. Because the reloader is disabled, stop and restart after editing Python code.

The API probe does **not** need the browser server. Every `python lab_client.py ...` command starts with a fresh temporary database. Repeated requests within one `--repeat` command share one application and rate-limit budget. A separate command resets them. Browser requests use the separate persistent `instance/notes.sqlite` database.

Reset the browser data only when needed (this removes this exercise's local note edits):

```bash
python -m flask --app app:create_app reset-db
```

For local use outside Codespaces, install Python 3.14, create a virtual environment with `python3.14 -m venv .venv`, activate it (`source .venv/bin/activate` on Linux/macOS, `.venv\Scripts\Activate.ps1` on PowerShell), and install `requirements.txt`. Open `http://127.0.0.1:5000`. Each exercise can run on its own with its own supplied requirements.

## Troubleshooting and working independently

- **`501` from Exercise 1:** the endpoint still contains its intentional `abort(501)` placeholder. Replace the whole matching function, including its body.
- **`403` while testing another control:** check the account role and CSRF header. `lab_client.py` supplies a valid token unless you ask for `--no-csrf`. Tests use valid prerequisites when testing ownership or validation.
- **`404` for an existing record:** this is the intended response for another owner's record. `999` is a missing ID and also returns `404`.
- **`415`:** the API expects a JSON content type. Use `--json` for normal examples, or deliberately use `--raw` to test malformed bodies.
- **`ModuleNotFoundError`:** verify the interpreter and run `python -m pip install -r requirements.txt` in the selected environment.
- **Port already in use / wrong application:** stop the previous `python app.py` with Ctrl+C. Check `pwd`, open a new terminal in this exercise folder, and restart. Browser cookies from another exercise may require signing in again.
- **Changes seem to disappear:** the probe and tests use temporary databases. For persistence use the browser, or `--inspect NOTE_ID` to inspect the same probe's database after its request.
- **Syntax/indentation error:** Python uses indentation for blocks. Functions inside `create_app` have four spaces, their bodies eight. In VS Code, undo the last paste and match the neighbouring route.
- **A test fails:** read the failing test name, then the `assert` and the actual value. Run just that test with `python -m pytest -q tests/test_api.py -k NAME`. A failed security assertion is different from an import or syntax error.

Work solo through the same predict, run, explain and repair sequence. Keep a small evidence record using `evidence.md`. If stuck, read the relevant completed function under the root `solutions/` directory, explain each line, and then implement it in your starter. You can run a solution independently. No earlier exercise is a prerequisite.
