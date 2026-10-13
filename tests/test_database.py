
import mysql.connector
import pytest

from modules import database as db


class FakeCursor:
    def __init__(self, rows=None, fail=False):
        self.rows, self.fail, self.executed, self.closed = rows or [], fail, [], False
        self.lastrowid = 7

    def execute(self, sql, params=None):
        if self.fail:
            raise mysql.connector.Error("boom")
        self.executed.append((sql, params))

    def fetchall(self):
        return self.rows

    def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, cursor):
        self._cursor, self.committed = cursor, False

    def cursor(self, dictionary=False):
        return self._cursor

    def commit(self):
        self.committed = True

    def close(self):
        pass


def test_save_uses_parameterized_query():
    cur = FakeCursor()
    conn = FakeConnection(cur)
    evil = "x'); DROP TABLE interactions; --"
    assert db.save_interaction(evil, "answer", connection=conn) == 7
    sql, params = cur.executed[0]
    assert "%s" in sql and evil not in sql
    assert params == (evil, "answer")
    assert conn.committed and cur.closed


def test_history_uses_parameterized_limit():
    rows = [{"id": 1, "user_input": "a", "ai_response": "b", "created_at": None}]
    cur = FakeCursor(rows=rows)
    assert db.get_history(5, connection=FakeConnection(cur)) == rows
    sql, params = cur.executed[0]
    assert "LIMIT %s" in sql and params == (5,)


def test_save_failure_raises_database_error():
    with pytest.raises(db.DatabaseError):
        db.save_interaction("a", "b", connection=FakeConnection(FakeCursor(fail=True)))


def test_history_failure_raises_database_error():
    with pytest.raises(db.DatabaseError):
        db.get_history(connection=FakeConnection(FakeCursor(fail=True)))


def test_connection_requires_configured_user(monkeypatch):
    monkeypatch.setenv("DB_USER", "")
    with pytest.raises(db.DatabaseError, match="not configured"):
        db.get_connection()


def test_connection_failure_is_friendly_and_hides_password(monkeypatch):
    monkeypatch.setenv("DB_USER", "someone")
    monkeypatch.setenv("DB_PASSWORD", "secret-pass")

    def fail(**kwargs):
        raise mysql.connector.Error("denied", errno=1045)

    monkeypatch.setattr(mysql.connector, "connect", fail)
    with pytest.raises(db.DatabaseError) as info:
        db.get_connection()
    assert "secret-pass" not in str(info.value)
    assert "username or password" in str(info.value)


def test_is_available_false_when_unconfigured(monkeypatch):
    monkeypatch.setenv("DB_USER", "")
    assert db.is_available() is False
