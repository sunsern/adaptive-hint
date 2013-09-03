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

# Server Configurations 
BIND_IP = '127.0.0.1'
LISTEN_PORT = 4350

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

        @add_handler(self.handlers, 'userinfo')
        def handle_userinfo(self, args): pass

    def on_open(self, info):
        """Callback for when a student is connected"""
        ActiveClients.students.add(self)
        logging.info("%s connected"%info.ip)

    def on_message(self, message):
        """Callback for when a message is received"""
        try:
            message = json.loads(message)
            f = self.handlers[message['command']]
            f(self, message['arguments'])
        except KeyError:
            pass
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

        @add_handler(self.handlers, 'list_student')
        def handle_list_student(self, args): pass
            

    def on_open(self, info):
        """Callback for when a teacher is connected"""
        ActiveClients.teachers.add(self)

    def on_message(self, message):
        """Callback for when a message is received"""
        try:
            message = json.loads(message)
            f = self.handlers[message['command']]
            f(self, message['arguments'])
        except KeyError:
            pass
        except Exception:
            import traceback
            traceback.print_exc()
            
    def on_close(self):
        """Callback for when a teacher is disconnected"""
        ActiveClients.teachers.remove(self)
        


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)

    # 1. Create routers
    StudentRouter = sockjs.tornado.SockJSRouter(StudentConnection, '/student')
    TeacherRouter = sockjs.tornado.SockJSRouter(TeacherConnection, '/teacher')

    # 2. Create Tornado application
    app = tornado.web.Application(StudentRouter.urls +
                                  TeacherRouter.urls)

    # 3. Make Tornado app listen on port 8080
    app.listen(LISTEN_PORT, address=BIND_IP)
    logging.info(" [*] Listening on %s:%d"%(BIND_IP,LISTEN_PORT))
    
    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()
