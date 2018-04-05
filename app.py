import tornado.ioloop
import tornado.web
import tornado.log
import os
import boto3

client = boto3.client(
  'ses',
  region_name='us-west-2',
  aws_access_key_id = 'AKIAIPBIR36FVIQVAGLQ',
  aws_secret_access_key = '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'
)

from jinja2 import \
  Environment, PackageLoader, select_autoescape

ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl):
    template = ENV.get_template(tpl)
    self.write(template.render())

class MainHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    
    self.render_template("index.html")
    
    
class PageHandler(TemplateHandler):
  def get(self, page):
    if page == 'form-complete':
      pass
    page = page + '.html'
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template(page)


class FormHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("form.html")
  
  def post(self):
    name = self.get_body_argument('name', None)
    email = self.get_body_argument('email', None)
    comment = self.get_body_argument('comment', None)
    rps = self.get_body_argument('rps', None)
    error = ''
    if name is not None and email is not None:
      response = client.send_email(
        Destination={
          'ToAddresses': ['CPGameface@gmail.com'],
        },
        Message={
          'Body': {
            'Text': {
              'Charset': 'UTF-8',
              'Data': '{} Sends a message.\n\n{}\n{}'.format(name, comment, rps),
            },
          },
          'Subject': {'Charset': 'UTF-8', 'Data': 'Test email'},
        },
        Source='CPGameface@gmail.com',
      )
      self.redirect('/form-complete')
    else:
      error = 'Please fill all required fields *'
      
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("form.html", {'error': error} ) 
    
def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/form", FormHandler),
    (r"/(form-complete)", PageHandler),
    (
      r"/static/(.*)",
      tornado.web.StaticFileHandler,
      {'path': 'static'}
    ),
  ], autoreload=True)
  
if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  PORT = int(os.environ.get('PORT', '8080'))
  app = make_app()
  app.listen(PORT)
  tornado.ioloop.IOLoop.current().start()