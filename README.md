# Week 9: API Security, Error Handling and Application Hardening

Develop a protected REST-style API, repair permission failures, create safe error responses and logs, then test browser hardening and rate limiting. This is a guided Flask/Jinja/SQLite lab for students with limited Flask experience.

## Start here

Accept the lecturer's classroom50 assignment link, open your resulting GitHub repository in Codespaces, and wait for the Python **3.14** container setup. Confirm `python --version`. Use the supplied container rather than an unrelated blank Codespace. Keep forwarded port 5000 **Private**.

Every folder below is a complete, independently runnable application. You do not need to copy code from an earlier task. Open its `INSTRUCTIONS.md`, then right-click that folder in Explorer and choose **Open in Integrated Terminal**. Run `python app.py`. Use a second terminal there for `python -m pytest -q` and the supplied `lab_client.py`. Stop the previous server before switching folders.

| Block | Task | Folder and instructions | Time |
|---|---|---|---:|
| 1 | Role refresher and permission parity | [Activity 1](block-1/activity-1-role-refresher/INSTRUCTIONS.md) | 25 min |
| 1 | Build API | [Exercise 1](block-1/exercise-1-build-api/INSTRUCTIONS.md) | 40 min |
| 1 | Fix API | [Exercise 2](block-1/exercise-2-fix-api/INSTRUCTIONS.md) | 30 min |
| 1 | Evaluate and design a test | [Evaluation](docs/BLOCK-1-EVALUATION.md) | 10 min |
| 2 | Error disclosure investigation | [Activity 2 worksheet](block-2/ACTIVITY-2-DISCLOSURE.md) | 20 min |
| 2 | Error handling and logging | [Exercise 3](block-2/exercise-3-error-handling/INSTRUCTIONS.md) | 45 min |
| 2 | Hardening | [Exercise 4](block-2/exercise-4-hardening/INSTRUCTIONS.md) | 30 min |
| 2 | Evaluate controls | [Evaluation](docs/BLOCK-2-EVALUATION.md) | 10 min |

Each block also includes a 10-minute introduction and 5-minute review. Instructions explain the concepts without requiring the lecturer's introduction. Collaborative activities work with two pairs and one group of three, with rotating roles, or can be completed solo.

## Accounts, policy and code guide

## Scenario and policy

Private Notes is a small internal planning application. A Jinja web page and a JSON API access the same SQLite records. The two interfaces must implement the same policy.

| Username | Role | Own note | Read own note | Edit own note | Access another owner's note |
|---|---|---:|---|---|---|
| `reader` | `viewer` | 1 | Yes | No | No |
| `editor` | `editor` | 2 | Yes | Yes | No |
| `other_editor` | `editor` | 3 | Yes | Yes | No |
| `admin` | `admin` | 4 | Yes | Yes | No |

All four fictional accounts use `Classroom-Only-314!`. Do not reuse this password elsewhere. Unknown roles receive no permission. In this deliberately narrow policy, **admin does not override ownership**. No interface permits changing `owner_id` or `is_reviewed`. A role permission answers “may this user perform this operation?” Ownership answers “on this record?”

Roles are reloaded from the database for each request. Client JSON cannot assign a role. The session cookie holds the user ID and CSRF token and is signed, not encrypted. It must not contain a password or private note.

## How the supplied application works

| File or folder | Purpose | How to read it |
|---|---|---|
| `app.py` | Configuration, web routes, API routes, error handlers | Read `create_app()` from top to bottom. A factory is just a function that builds and returns an application. |
| `db.py` | SQLite schema, seed data and query functions | `find_note(id)` returns a row or `None`. `update_note` changes only title/content using SQL placeholders. |
| `security.py` | Role, ownership, CSRF and validation helpers | Functions return a Boolean, return validated data, or stop the request with `abort`. |
| `templates/` | Login and notes pages | Jinja inserts values with `{{ ... }}` and controls loops/conditions with `{% ... %}`. HTML text is escaped automatically. |
| `static/style.css` | Small stylesheet | Kept outside the HTML so the supplied CSP permits it. No JavaScript is required. |
| `lab_client.py` | Repeatable HTTP examples without a running server | Logs in through the real login route and supplies the resulting CSRF token. |
| `tests/` | Checks using Flask's test client | Each test uses a fresh temporary database. Tests never change browser data. |
| `instance/` | Browser application's generated database | Created when you run the app. Ignored by Git. |

`@app.get(...)` registers the function beneath it as a route. `<int:note_id>` converts a URL segment to an integer argument. `g.user` is the user loaded for this request. `session` persists small signed values across requests. `jsonify` creates a JSON response with the correct content type. `return response, 403` sets an HTTP status; returning an error message alone can accidentally send `200`.

A SQLite row supports `note["title"]` like a dictionary, but is not itself a JSON response. `public_note` deliberately selects the response fields. The `?` in SQL is a value placeholder: the SQLite driver binds supplied values instead of constructing SQL by concatenation.

## Solutions and evidence

Completed solutions can be found in the lab template repository's [`solutions` branch](https://github.com/SERC-Sec-Prog-DF1A-2627/Lab---API-Security-Error-Handling-and-Application-Hardening/tree/solutions/solutions). Use them to learn, and record any reference use in each exercise's `evidence.md`. The emphasis is explanation and test evidence, not simply obtaining a green summary.

[Expected test results](docs/EXPECTED-TEST-RESULTS.md) distinguishes deliberate starter failures from setup errors. [Concept notes](docs/CONCEPT-NOTES.md) explains Flask, Jinja, dictionaries, decorators, HTTP, CSRF and testing. [Troubleshooting](docs/TROUBLESHOOTING.md) covers common problems. Do not run pytest across all applications together; run it in one folder.

## Environment details

Dependencies are pinned in `requirements.txt`; `requirements.in` identifies the three direct dependencies. Each application includes a copy of the dependency lock so it can be run separately. The devcontainer uses the Python 3.14 image family. Stop the Flask development server when finished and stop the Codespace to avoid consuming further compute time.

The learning application intentionally omits production account lifecycle, password reset, central log collection, distributed rate limiting and deployment infrastructure. It has no real users or confidential records. Exercise 2 and Exercise 3 contain explicitly labelled vulnerabilities to repair.
