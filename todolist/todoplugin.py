from maubot import Plugin, MessageEvent
from maubot.handlers import command
from mautrix.types import EventType

from todolist.database import TodoListDatabase


class TodoListPlugin(Plugin):
    db: TodoListDatabase

    async def start(self) -> None:
        self.db = TodoListDatabase(self.database, self)

    @command.new("todo", require_subcommand=False, help="Zeigt die Todoliste für diesen Raum an.")
    async def todo(self, evt: MessageEvent) -> None:
        todo_list: dict = self.db.get_todo(evt.room_id)
        if len(todo_list) == 0:
            await evt.respond("Die Todoliste hat keine Einträge. Erstelle einen mit `!todo add <Eintrag>`")
        else:
            todo: str = ""
            for index, todo_id in enumerate(sorted(todo_list)):
                todo = todo + f"{index + 1}. {todo_list[todo_id]} - ID: {todo_id}\n"
            await evt.respond(f"**Todo-Liste:**\n\n{todo}")

    @todo.subcommand("add", help="Fügt einen Eintrag zur Todoliste dieses Raumes hinzu.", aliases=["new", "put"])
    @command.argument("todo", required=True, pass_raw=True)
    async def todo_add(self, evt: MessageEvent, todo: str) -> None:
        if todo == "":
            await evt.respond("Du musst einen Inhalt angeben: `!todo add <INHALT>`")
        else:
            self.db.add_todo(evt.room_id, todo)
            await evt.respond(f"Du hast \"{todo}\" zur Todoliste hinzugefügt.")

    @todo.subcommand("remove", help="Entfernt einen Eintrag aus der Todoliste dieses Raumes",
                     aliases=["delete", "rem", "finish"])
    @command.argument("todo", required=True, pass_raw=False)
    async def todo_remove(self, evt: MessageEvent, todo: str):
        try:
            todo_id = int(todo)
            if not self.db.todo_entry_exsists(evt.room_id, todo_id):
                raise ValueError()
            self.db.remove_todo(evt.room_id, todo_id)
            await evt.respond(f"Du hast den Eintrag mit der ID {todo_id} von der Todoliste entfernt.")
        except ValueError:
            await evt.respond("Du musst eine gültige ID angeben!")

    @todo.subcommand("clear", help="Leert die Todoliste von diesem Raum.", aliases=["flush", "drop", "finishall"])
    async def todo_clear(self, evt: MessageEvent) -> None:
        levels = await self.client.get_state_event(evt.room_id, EventType.ROOM_POWER_LEVELS)
        user_level = levels.get_user_level(evt.sender)
        if user_level < 50:
            await evt.respond("Du musst mindestens Powerlevel 50 haben, um die Todoliste zu leeren.")
        else:
            self.db.clear_todo(evt.room_id)
            await evt.respond("Die Todoliste wurde geleert.")
