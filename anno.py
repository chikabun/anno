import os

from urllib.parse import urlparse
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect

from jinja2 import Environment, FileSystemLoader

class Student:

    def __init__(self, config):
        self.age = config["age"]
        self.name = config.get("name")

    def do_something(self, times):
        result = "";
        for _ in range(times):
            result += self.name + " "
        return result

    def __str__(self):
        return f"=== {self.name} {self.age} ==="

    # def wsgi_app(self, environ, start_response):
    #     request = Request(environ)
    #     response = self.dispatch_request(request)
    #     return response(environ, start_response)

    # def __call__(self, environ, start_response):
    #     return self.wsgi_app(environ, start_response)

object1 = Student({"age": 18, "name": "Denis Bushtruk"})
object2 = Student({"age": 19, "name": "Julia Bu"})

print(object1)
print(object1.age)
print(object1.name)
print(object1.do_something(3))

print(object2)
print(object2.age)
print(object2.name)
print(object2.do_something(4))
