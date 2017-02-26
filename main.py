#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "template")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title=db.StringProperty(required = True)
    blog=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)

class MainPage(Handler):
    def render_main(self, error = ""):
        blogs = db.GqlQuery("Select * from Blog Order By created DESC Limit 5")  

        self.render("mainblog.html", error=error, blogs=blogs)
    
    def get(self):
        self.render_main()

   
class NewPost(Handler):
    def render_newpost_form(self, title="", blog = "", error = ""):
        self.render("newpost.html", title=title, blog=blog, error=error)

    def get(self):
        self.render_newpost_form()

    def post(self): 
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            a = Blog(title=title, blog=blog)
            a.put()
            blog_id=a.key().id()

            self.redirect("/blog/"+str(blog_id))
        else:
            error = "You need to add both a title and blog"
            self.render_newpost_form(title, blog, error)

       

class ViewPostHandler(Handler):
    def get(self, id):
        blog_post = Blog.get_by_id(int(id))
        self.render("singlepost.html", title=blog_post.title, blog=blog_post.blog)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
