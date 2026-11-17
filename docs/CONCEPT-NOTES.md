# Concept notes: reading the supplied Python and HTTP code

## Web pages and APIs

A browser page sends HTML for a person to view. An API sends structured data for a client to process. Both are HTTP interfaces. A request includes a method, path, headers and sometimes a body. A response includes a status, headers and body. The same login session can be used by either interface; choosing JSON does not change who may access data.

GET should retrieve without changing application state. PATCH changes selected fields. Our PATCH is an ordinary JSON object designed for this exercise; it does not implement the separate JSON Patch standard. A JSON Content-Type tells Flask how to parse bytes, not whether values are trusted.

## Dictionaries, rows and Boolean helpers

```python
changes = {"title": "Plan", "content": "Draft"}
print(changes["title"])            # Key lookup: Plan
print(changes.get("owner_id", 2)) # Missing key uses default: 2
allowed = {"title", "content"}    # A set, not a dictionary
unexpected = set(changes) - allowed
```

A dictionary maps keys to values. An SQLite Row is a database result supporting named column access. A set contains unique values and supports set difference. JSON has objects, arrays, strings, numbers, booleans and null; JSON `null` becomes Python `None`. Validate the outer type before using dictionary operations.

`def can_edit_notes(user):` names a function and parameter. A caller supplies the argument in `can_edit_notes(g.user)`. The return value is a Boolean. An `if` decides whether to execute its indented block. `and` short-circuits, allowing a `None` check before a field lookup. There is no need for a custom `*args, **kwargs` permission decorator in these exercises.

## Decorators and factory scope

A decorator applies to the function immediately below it. Flask uses a route decorator to associate a URL/method with a function. Flask-Limiter wraps that function to enforce a budget. Keep the supplied decorator order. The `create_app` function returns a new Flask application; tests call it for isolation. Route functions are nested inside it, so indentation is significant. This is a small testing convenience, not a framework layer you need to design.

## Templates and data

Jinja `{{ note['title'] }}` substitutes a value, `{% for note in notes %}` repeats a section, and `{% if can_edit_notes(user) %}` controls whether to show a form. Flask autoescapes ordinary HTML template values. Keep attributes quoted, avoid `|safe` on untrusted content, and remember that hiding a form does not block HTTP requests.

## Authentication, operation, object and property permissions

Authentication identifies the signed-in user. The role helper decides whether the operation is permitted. Ownership restricts which note is in scope. The input field allowlist restricts properties the user may change; the response allowlist restricts properties they may see. SQL parameterisation prevents values becoming SQL syntax. These controls have separate jobs.

## CSRF and cookie settings

A browser may automatically send a cookie. A CSRF token binds a state-changing request to a session-aware client. This app stores a random token in the signed session and compares it with a form field or X-CSRF-Token header. The token is rotated on login. SameSite and HttpOnly help in different ways: SameSite affects cross-site cookie transmission and HttpOnly prevents JavaScript reading the cookie. Neither performs ownership checks. Secure requires HTTPS. A signed cookie is readable to the user, so signing is not encryption.

## Exceptions, status and logs

Expected request errors have a meaningful 4xx status; unexpected application failures use 500. The handler sends controlled wording and a server-generated correlation ID. The application log stores named fields, not raw requests. A log is useful only if the right people can safely inspect it and somebody monitors relevant events.

## Tests as security arguments

Arrange a meaningful identity and resource, act through the real HTTP route, then assert response and state. Include allowed and denied cases. A negative test must satisfy unrelated prerequisites: otherwise, a CSRF failure can disguise a missing ownership check. Fixtures are reusable setup; a fresh database prevents one test's changes influencing another. Inspect failing assertions before editing the implementation.

## Further reading

- [Flask quickstart](https://flask.palletsprojects.com/en/stable/quickstart/) for routes, responses and sessions.
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/) for test clients and fixtures.
- [OWASP API Security Top 10, 2023 edition](https://api-security.owasp.org/editions/2023/en/0x11-t10/) for API risk categories.
- [Flask security considerations](https://flask.palletsprojects.com/en/stable/web-security/) and [error handlers](https://flask.palletsprojects.com/en/stable/errorhandling/).
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).
- [Flask-Limiter documentation](https://flask-limiter.readthedocs.io/en/stable/) for limit configuration and storage.

The concrete accounts, policy, code and request examples in this pack are teaching examples. References checked 17 November 2026.
