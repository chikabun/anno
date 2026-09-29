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

class Anno:
    def __init__(self):

        self.jinja_env = Environment(
            loader=FileSystemLoader(os.path.join(".", "templates")),
            autoescape=True
        )

        self.url_map = Map(
            [
                # Pages for testing
                # Rule("/testing_post", endpoint="testing_post"), # show tester for POST requests
                # Rule("/testing_get", endpoint="testing_get"), # show tester for GET requests

                # Admin
                Rule("/", endpoint="admin_login"),
                # Rule("/admin", endpoint="admin_login"),
                # Rule("/admin_submit_password", endpoint="admin_submit_password"),
                # Rule("/admin_logout", endpoint="admin_logout"),
                # Rule("/admin_clear_cache", endpoint="admin_clear_cache"),
                # Rule("/admin_main", endpoint="admin_main"),
                # Rule("/admin_change_settings", endpoint="admin_change_settings"),

                # # Web Service
                # Rule("/g", endpoint="generate"),
                # Rule("/login", endpoint="login"),
            ]
        )

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype="text/html")

    def on_admin_login(self, request):
        return self.render_template(
            "admin_login.html",
            timestamp=time.time(),
            message="Enter login and password"
        )

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
            "/static": os.path.join(".", "static"),
        }
    )
    run_simple("0.0.0.0", 5555, app, use_debugger=True, use_reloader=True)

