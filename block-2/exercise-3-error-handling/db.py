"""Small SQLite helpers. Each application has its OWN instance/notes.sqlite.
SQL uses ? placeholders for values. No ORM or shared database is required.
"""
from pathlib import Path
import sqlite3
from flask import current_app, g
from werkzeug.security import generate_password_hash

DEMO_PASSWORD = "Classroom-Only-314!"  # Fictional accounts for this private lab only.


def get_db():
    # g lasts for one request (or application context). Reuse its connection.
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # row["title"] is clearer than row[2].
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    """Destructively reset ONLY this application's configured lab database."""
    path = Path(current_app.config["DATABASE"])
    path.parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.executescript("""
        DROP TABLE IF EXISTS notes;
        DROP TABLE IF EXISTS users;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        );
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY,
            owner_id INTEGER NOT NULL REFERENCES users(id),
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            is_reviewed INTEGER NOT NULL DEFAULT 0 CHECK(is_reviewed IN (0,1))
        );
    """)
    accounts = [(1,"reader","viewer"), (2,"editor","editor"),
                (3,"other_editor","editor"), (4,"admin","admin")]
    password_hash = generate_password_hash(DEMO_PASSWORD)
    for uid, username, role in accounts:
        db.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                   (uid, username, password_hash, role))
        db.execute("INSERT INTO notes VALUES (?, ?, ?, ?, 0)",
                   (uid, uid, f"{username}'s plan", "Draft for the teaching lab."))
    db.commit()


def find_user(username):
    return get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def user_by_id(user_id):
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def find_note(note_id):
    return get_db().execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()


def notes_for(user_id):
    return get_db().execute("SELECT * FROM notes WHERE owner_id = ? ORDER BY id", (user_id,)).fetchall()


def update_note(note_id, owner_id, title, content):
    # Ownership appears again in the UPDATE as defence in depth.
    db = get_db()
    cursor = db.execute("UPDATE notes SET title = ?, content = ? WHERE id = ? AND owner_id = ?",
                        (title, content, note_id, owner_id))
    db.commit()
    return cursor.rowcount


def legacy_update(note_id, values):
    """INTENTIONALLY UNSAFE field permissions, used only by Exercise 2 starter.
    Values are still parameterised: this lesson is about mass assignment,
    not SQL injection. All column names below are fixed in source code.
    """
    db = get_db()
    db.execute("UPDATE notes SET title=?, content=?, owner_id=?, is_reviewed=? WHERE id=?",
               (values["title"], values["content"], values["owner_id"], values["is_reviewed"], note_id))
    db.commit()
