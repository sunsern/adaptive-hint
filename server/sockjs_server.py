"""
SockJS server for the adaptive hint project.

The server binds to a specific IP address and listens on a specific
port. It responses to the requests from SockJS clients.
"""
import tornado.ioloop
import tornado.web
import sockjs.tornado
import json
import logging
import urllib
import urllib2

# Server Configurations 
BIND_IP = '0.0.0.0'
LISTEN_PORT = 4350
REST_API = 'http://localhost:4351'

def add_handler(handlers, command):
    """Decorative function for adding a command handler."""
    def handler(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
        handlers[command] = wrapper    
        return wrapper
    return handler


class ActiveClients(object):
    """Keeps track of opened clients for both students and teachers"""
    students = set()
    teachers = set()


class StudentConnection(sockjs.tornado.SockJSConnection):
    """Student connection implementation""" 
   
    def __init__(self, *args, **kwargs):
        super(StudentConnection, self).__init__(*args, **kwargs)
        self.student_id = ''
        self.student_name = ''
        self.pg_path = ''
        self.pg_source = ''

        #define message handlers
        self.handlers = {}

        @add_handler(self.handlers, 'keypressed')
        def handle_keypressed(self, args): pass

        @add_handler(self.handlers, 'checkanswer')
        def handle_checkanswer(self, args): pass

        @add_handler(self.handlers, 'student_info')
        def handle_student_info(self, args):
            self.student_name = args['name']
            self.pg_path = ("/opt/webwork/courses/UCSD_CSE103/templates/" +
                            args['pg'])
            
    def on_open(self, info):
        """Callback for when a student is connected"""
        ActiveClients.students.add(self)
        logging.info("%s connected"%info.ip)

    def on_message(self, message):
        """Callback for when a message is received"""
        try:
            message = json.loads(message)
            logging.info("[%s] student command: %s"%(
                self.session.conn_info.ip,
                message['command']))
            f = self.handlers[message['command']]
            f(self, message['arguments'])
        except KeyError:
            logging.warning("unhandled command")
        except Exception:
            import traceback
            traceback.print_exc()
            
    def on_close(self):
        """Callback for when a student is disconnected"""
        ActiveClients.students.remove(self)


class TeacherConnection(sockjs.tornado.SockJSConnection):
    """Teacher connection implementation"""
    
    def __init__(self, *args, **kwargs):
        super(TeacherConnection, self).__init__(*args, **kwargs)
        
        # Define message handlers
        self.handlers = {}

        @add_handler(self.handlers, 'list_students')
        def handle_list_student(self, args):
            """
            """
            names = [s.student_name for s in ActiveClients.students]
            self.send(json.dumps(names))

        @add_handler(self.handlers, 'send_hint')
        def handle_send_hint(self, args):
            hint = "<div>hint</div>"
            self.broadcast(ActiveClients.students, hint)
            
        @add_handler(self.handlers, 'render_hint')
        def handle_render_hint(self, args):
            url = REST_API + "/render"
            values = {'somekey':'somevalue'}
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)
            response = urllib2.urlopen(req)
            self.send(response.read())
            
    def on_open(self, info):
        """Callback for when a teacher is connected"""
        ActiveClients.teachers.add(self)

    def on_message(self, message):
        """Callback for when a message is received"""
        try:
            message = json.loads(message)
            logging.info("[%s] teacher command: %s"%(
                self.session.conn_info.ip,
                message['command']))
            f = self.handlers[message['command']]
            f(self, message['arguments'])
        except KeyError:
            logging.warning("unhandled command")
        except Exception:
            import traceback
            traceback.print_exc()
            
    def on_close(self):
        """Callback for when a teacher is disconnected"""
        ActiveClients.teachers.remove(self)
        

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    # Create routers
    StudentRouter = sockjs.tornado.SockJSRouter(StudentConnection, '/student')
    TeacherRouter = sockjs.tornado.SockJSRouter(TeacherConnection, '/teacher')

    # Create Tornado application
    app = tornado.web.Application(StudentRouter.urls +
                                  TeacherRouter.urls)

    # Make Tornado app listen on port 8080
    app.listen(LISTEN_PORT, address=BIND_IP)
    logging.info(" [*] Listening on %s:%d"%(BIND_IP,LISTEN_PORT))
    
    # Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
