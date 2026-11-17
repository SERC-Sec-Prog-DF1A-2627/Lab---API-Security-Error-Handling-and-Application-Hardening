# Completed reference: exercise-3

This is an independently runnable completed application with its own database and tests. From this folder:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python lab_client.py
python app.py
```

Use Python 3.14. Stop another exercise's server before starting port 5000. The browser port must remain private. Reset this folder's browser database with `python -m flask --app app:create_app reset-db` (removes local note edits).

The detailed walkthrough is in [the matching student exercise](../../block-2/exercise-3-error-handling/INSTRUCTIONS.md). Compare functions, not generated database files. This solution uses the same tests as the starter. All supplied tests should pass.

The four fictional users and policies are documented in [the repository guide](../../README.md). The API probe uses a fresh temporary database on every invocation, independent of browser data.
