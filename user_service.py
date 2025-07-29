import tornado.web
import tornado.log
import tornado.options
import sqlite3
import logging
import json
import time

class App(tornado.web.Application):
    def __init__(self, handlers, **kwargs):
        super().__init__(handlers, **kwargs)
        self.db = sqlite3.connect("listings.db")
        self.db.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self):
        cursor = self.db.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "created_at INTEGER NOT NULL,"
            "updated_at INTEGER NOT NULL"
            ");"
        )
        self.db.commit()

class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))

# /users
class UsersHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        page_num = int(self.get_argument("page_num", 1))
        page_size = int(self.get_argument("page_size", 10))

        limit = page_size
        offset = (page_num - 1) * page_size

        cursor = self.application.db.cursor()
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))

        users = []
        for row in cursor.fetchall():
            users.append({
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            })

        self.write_json({"result": True, "users": users})

    @tornado.gen.coroutine
    def post(self):
        name = self.get_argument("name", None)
        if not name:
            self.write_json({"result": False, "errors": ["name is required"]}, status_code=400)
            return

        time_now = int(time.time() * 1e6)

        cursor = self.application.db.cursor()
        cursor.execute(
            "INSERT INTO users (name, created_at, updated_at) VALUES (?, ?, ?)",
            (name, time_now, time_now)
        )
        self.application.db.commit()

        user_id = cursor.lastrowid
        if not user_id:
            self.write_json({"result": False, "errors": ["Failed to create user"]}, status_code=500)
            return

        self.write_json({
            "result": True,
            "user": {
                "id": user_id,
                "name": name,
                "created_at": time_now,
                "updated_at": time_now
            }
        })

# /users/{id}
class UserByIdHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self, user_id):
        try:
            user_id = int(user_id)
        except ValueError:
            self.write_json({"result": False, "errors": ["invalid user_id"]}, status_code=400)
            return

        cursor = self.application.db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            self.write_json({"result": False, "errors": ["user not found"]}, status_code=404)
            return

        self.write_json({
            "result": True,
            "user": {
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
        })

# /users/ping
class PingHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.write("pong!")

def make_app(options):
    return App([
        (r"/users/ping", PingHandler),
        (r"/users", UsersHandler),
        (r"/users/([0-9]+)", UserByIdHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    tornado.options.define("port", default=7000)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.listen(options.port)
    logging.info("Starting user service. PORT: {}, DEBUG: {}".format(options.port, options.debug))
    tornado.ioloop.IOLoop.instance().start()
