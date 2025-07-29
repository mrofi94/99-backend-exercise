import tornado.web
import tornado.httpclient
import tornado.options
import tornado.gen
import logging
import json

class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))

# /public-api/ping
class PingHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        self.write("pong!")

# /public-api/users
class PublicUsersHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        http_client = tornado.httpclient.AsyncHTTPClient()
        url = "http://localhost:7000/users"
        params = self.request.query
        if params:
            url += "?" + params

        try:
            response = yield http_client.fetch(url)
            self.write_json(json.loads(response.body.decode()))
        except Exception as e:
            logging.exception("Failed to fetch users")
            self.write_json({"result": False, "errors": ["Internal error fetching users"]}, status_code=500)

    @tornado.gen.coroutine
    def post(self):
        body = json.loads(self.request.body)
        name = body.get("name")

        if not name:
            self.write_json({"result": False, "errors": ["name is required"]}, status_code=400)
            return

        http_client = tornado.httpclient.AsyncHTTPClient()
        try:
            response = yield http_client.fetch(
                "http://localhost:7000/users",
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                body=f"name={name}"
            )
            self.write_json(json.loads(response.body.decode()))
        except Exception as e:
            logging.exception("Failed to create user")
            self.write_json({"result": False, "errors": ["Internal error creating user"]}, status_code=500)

# /public-api/listings
class PublicListingsHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        http_client = tornado.httpclient.AsyncHTTPClient()
        listings_url = "http://localhost:6000/listings"
        users_url = "http://localhost:7000/users"

        # Forward query string to listings
        listings_url += "?" + self.request.query if self.request.query else ""

        try:
            # Fetch listings
            listings_response = yield http_client.fetch(listings_url)
            listings_data = json.loads(listings_response.body.decode())

            # Fetch users (all, to match listing user_id)
            users_response = yield http_client.fetch(users_url)
            users_data = json.loads(users_response.body.decode())

            user_map = {user["id"]: user for user in users_data.get("users", [])}

            # Enrich listings with user info
            for listing in listings_data.get("listings", []):
                user = user_map.get(listing["user_id"])
                listing["user"] = user if user else {}

            self.write_json(listings_data)
        except Exception as e:
            logging.exception("Failed to fetch public listings")
            self.write_json({"result": False, "errors": ["Internal error fetching listings"]}, status_code=500)

    @tornado.gen.coroutine
    def post(self):
        try:
            body = json.loads(self.request.body)
            user_id = body.get("user_id")
            listing_type = body.get("listing_type")
            price = body.get("price")

            # Basic validation
            if not user_id or not listing_type or not price:
                self.write_json({"result": False, "errors": ["Missing required fields"]}, status_code=400)
                return

            # Forward to listing service
            http_client = tornado.httpclient.AsyncHTTPClient()
            response = yield http_client.fetch(
                "http://localhost:6000/listings",
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                body=f"user_id={user_id}&listing_type={listing_type}&price={price}"
            )
            self.write_json(json.loads(response.body.decode()))
        except Exception as e:
            logging.exception("Failed to create listing")
            self.write_json({"result": False, "errors": ["Internal error creating listing"]}, status_code=500)

def make_app(options):
    return tornado.web.Application([
        (r"/public-api/ping", PingHandler),
        (r"/public-api/users", PublicUsersHandler),
        (r"/public-api/listings", PublicListingsHandler),
    ], debug=options.debug)

if __name__ == "__main__":
    tornado.options.define("port", default=8000)
    tornado.options.define("debug", default=True)
    tornado.options.parse_command_line()
    options = tornado.options.options

    app = make_app(options)
    app.listen(options.port)
    logging.info("Starting public API. PORT: {}, DEBUG: {}".format(options.port, options.debug))
    tornado.ioloop.IOLoop.instance().start()
