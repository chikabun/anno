import os
import time

from urllib.parse import urlparse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect
from werkzeug.serving import run_simple

from jinja2 import Environment
from jinja2 import FileSystemLoader

import anno_db

# project root : one level above the "src" folder
# get dir from dir
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTL_ADMIN_SESSION = 3600

class Anno:
    def __init__(self):

        self.mysql = anno_db.AnnoDB(session_ttl_seconds=TTL_ADMIN_SESSION)

        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(PROJECT_DIR, "templates")),
            autoescape=True
        )

        self.url_map = Map(
            [
                # Pages for testing
                # Rule("/testing_post", endpoint="testing_post"), # show tester for POST requests
                # Rule("/testing_get", endpoint="testing_get"), # show tester for GET requests

                # Admin
                Rule("/", endpoint="admin_login"),
                Rule("/admin", endpoint="admin_login"),
                Rule("/admin_submit_password", endpoint="admin_submit_password"),
                # Rule("/admin_logout", endpoint="admin_logout"),
                # Rule("/admin_clear_cache", endpoint="admin_clear_cache"),
                Rule("/admin_main", endpoint="admin_main"),
                # Rule("/admin_change_settings", endpoint="admin_change_settings"),

                # # Web Service
                # Rule("/g", endpoint="generate"),
                # Rule("/login", endpoint="login"),
            ]
        )

    def on_admin_submit_password(self, request):
        if request.method != "POST":
            return Response(
                response=json.dumps({
                    "error": 1,
                    "message": "POST required"
                }),
                mimetype="application/json",
                status=405
            )

        data = request.form
        login = data.get("username")
        password = data.get("password")

        u = self.mysql.get_user_by_login_and_password(login, password)
        if u is None:
            return self.render_template(
                "admin_login.html",
                timestamp=time.time(),
                message="Wrong login or password"
            )

        session_id = self.mysql.create_session(u['id'])
        if session_id is None:
            return self.render_template(
                "admin_login.html",
                timestamp=time.time(),
                message="Unable to create a session record"
            )

        response = redirect("/admin_main")
        response.set_cookie(
            "session_id",
            session_id,
            max_age=self.mysql.session_ttl,
            httponly=True,
            samesite="Strict"
        )
        return response

    def on_admin_login(self, request):
        return self.render_template(
            "admin_login.html",
            timestamp=time.time(),
            message="Enter login and password"
        )

    def on_admin_main(self, request):
        # check session first
        session_id = request.cookies.get("session_id")
        user_id = self.mysql.get_session(session_id) if session_id else None

        if user_id is None:
            return redirect("/admin")

        user = self.mysql.get_user_by_id(user_id)
        task_count = self.mysql.get_task_count_for_user(user_id)
        all_settings = self.mysql.get_settings(user_id)

        if all_settings is None:
            all_settings = {}

        return self.render_template(
            "admin_main.html",
            timestamp=time.time(),
            welcome_message="Welcome " + user["username"] + " (" + user["email"] + ")",
            show_logout_link=True,
            tasks_for_this_user=task_count,
            hint_for_settings="11111111111111111111111111",
            all_settings=all_settings, # attach the whole dictionary
        )

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype="text/html")

    def error_404(self):
        response = self.render_template("404.html") 
        response.status_code = 404
        return response

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, f"on_{endpoint}")(request, **values)
        except NotFound:
            return self.error_404()
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


if __name__ == "__main__":
    app = Anno()
    app.wsgi_app = SharedDataMiddleware(
        app.wsgi_app,
        {
            "/static": os.path.join(PROJECT_DIR, "static"),
        }
    )
    run_simple("0.0.0.0", 5555, app, use_debugger=True, use_reloader=True)

