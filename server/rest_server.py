import tornado.ioloop
import tornado.web
import logging
 
# Server configuration
BIND_IP = '0.0.0.0'
LISTEN_PORT = 4351

class PGHandler(tornado.web.RequestHandler):
    def get(self):
        response = { 'version': '3.5.1',
                     'last_build':  date.today().isoformat() }
        self.write(response)
 
class HintHandler(tornado.web.RequestHandler):
    def get(self, id):
        response = { 'id': int(id),
                     'name': 'Crazy Game',
                     'release_date': date.today().isoformat() }
        self.write(response)

class RenderHandler(tornado.web.RequestHandler):
    def get(self, id):
        response = { 'id': int(id),
                     'name': 'Crazy Game',
                     'release_date': date.today().isoformat() }
        self.write(response)
 
class CheckAnswerHandler(tornado.web.RequestHandler):
    def post(self, id):
        response = { 'id': int(id),
                     'name': 'Crazy Game',
                     'release_date': date.today().isoformat() }
        self.write(response)
        
    
application = tornado.web.Application([
        (r"/pg/([0-9]+)", PGHandler),
        (r"/hints", HintHandler)
        ])
 
if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    application.listen(LISTEN_PORT, address=BIND_IP)
    logging.info(" [*] Listening on %s:%d"%(BIND_IP,LISTEN_PORT))
    
    tornado.ioloop.IOLoop.instance().start()
