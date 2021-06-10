import operator
from typing import Dict

from maubot import Plugin
from sqlalchemy import (Column, String, Integer, Table, MetaData, and_, Text)
from sqlalchemy.engine.base import Engine


class TodoListDatabase:
    todos: Table
    db: Engine
    plugin: Plugin

    def __init__(self, db: Engine, plugin: Plugin) -> None:
        self.db = db
        self.plugin = plugin

        meta = MetaData()
        meta.bind = db

        self.todos = Table("todo_list", meta,
                           Column("id", Integer, primary_key=True, autoincrement=True),
                           Column("room_id", String(255), nullable=False),
                           Column("content", Text, nullable=False))
        meta.create_all()

    def add_todo(self, room_id: str, content: str):
        self.db.execute(self.todos.insert().values(room_id=room_id, content=content))

    def remove_todo(self, room_id: str, todo_id: int):
        self.db.execute(self.todos.delete().where(and_(self.todos.c.room_id == room_id, self.todos.c.id == todo_id)))

    def get_todo(self, room_id: str) -> dict:
        todo_list = {}
        todos = self.db.execute(self.todos.select().where(self.todos.c.room_id == room_id)).fetchall()
        for todo in todos:
            todo_list[todo.id] = todo.content
        return todo_list

    def todo_entry_exsists(self, room_id: str, todo_id: int) -> bool:
        return self.db.execute(self.todos.select().where(
            and_(self.todos.c.room_id == room_id, self.todos.c.id == todo_id))).fetchone() is not None

    def clear_todo(self, room_id: str):
        self.db.execute(self.todos.delete().where(self.todos.c.room_id == room_id))
