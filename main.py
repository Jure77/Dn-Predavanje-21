#!/usr/bin/env python
import os
import jinja2
import webapp2

from google.appengine.api import users

from models import Message


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            sign_in = True
            logout_url = users.create_logout_url("/")
            output = {
                "user": user,
                "sign_in": sign_in,
                "logout_url": logout_url,
            }
        else:
            sign_in = False
            login_url = users.create_login_url("/")
            output = {
                "user": user,
                "sign_in": sign_in,
                "login_url": login_url,
            }

        return self.render_template("hello.html", output)

class ShraniHandler(BaseHandler):

    def post(self):
        ime = self.request.get("ime")
        priimek = self.request.get("priimek")
        email = self.request.get("email")
        sporocilo = self.request.get("sporocilo")

        if "<script>" in sporocilo:
            return self.write("Nice try!")

        # shrani sporocilo v bazo.
        spr = Message(ime=ime, priimek=priimek, email=email, sporocilo=sporocilo)
        spr.put()

        return self.render_template("shrani.html")

class VsaSporocilaHandler(BaseHandler):
    def get(self):
        sporocila = Message.query().fetch()
        spremenljivke = {
            "sporocila": sporocila
        }
        return self.render_template("seznam.html", spremenljivke)

class GuestBookHandler(BaseHandler):
    def get(self):
        return self.render_template("guest.html")

class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Message.get_by_id(int(sporocilo_id))
        spremenljivke = {
            "sporocilo": sporocilo
        }
        return self.render_template("posamezno-sporocilo.html", spremenljivke)

class UrediSporociloHandler(BaseHandler):
    def get (self, sporocilo_id):
        sporocilo = Message.get_by_id(int(sporocilo_id))
        spremenljivke = {
            "sporocilo": sporocilo
        }
        return self.render_template("uredi-sporocilo.html", spremenljivke)

    def post(self, sporocilo_id):
        sporocilo = Message.get_by_id(int(sporocilo_id))
        sporocilo.ime = self.request.get("ime")
        sporocilo.priimek = self.request.get("priimek")
        sporocilo.email = self.request.get("email")
        sporocilo.sporocilo = self.request.get("sporocilo")
        sporocilo.put()

        return self.redirect("/vsa-sporocila")

class IzbrisiSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = Message.get_by_id(int(sporocilo_id))
        spremenljivke = {
            "sporocilo": sporocilo
        }


        return self.render_template("izbrisi-sporocilo.html", spremenljivke)

    def post(self, sporocilo_id):
        sporocilo = Message.get_by_id(int(sporocilo_id))
        sporocilo.key.delete()

        return self.write("Izbrisano")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/save', ShraniHandler, name="shrani-stran"),
    webapp2.Route('/guestbook', GuestBookHandler),
    webapp2.Route('/vsa-sporocila', VsaSporocilaHandler),
    webapp2.Route('/posamezno-sporocilo/<sporocilo_id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/posamezno-sporocilo/<sporocilo_id:\d+>/uredi', UrediSporociloHandler),
    webapp2.Route('/posamezno-sporocilo/<sporocilo_id:\d+>/izbrisi', IzbrisiSporociloHandler),
], debug=True)
