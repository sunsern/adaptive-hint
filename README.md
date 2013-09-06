adaptive-hint
=============

Requirements
------------
```
sockjs-tornado==1.0.0
tornado==3.1.1
```


REST API [\[rest_server.py\]](https://github.com/sunsern/adaptive-hint/blob/master/server/rest_server/rest_server.py)
---------------------------------
#### PG Resources / Matt
  - ```POST /pg``` -- Retrieve PG source from a path 

#### Hint Resources /Matt
  - ```GET /hints/:pg_id``` -- Retrieve hints associated with the given pg_id
  - ```POST /hints/:pg_ig``` -- Add hints to the given pg_id
  - ```DELETE /hints/:hint_id``` -- Delete a hint

#### Render / Sunsern
  - ```POST /render``` -- Render HTML from PG
    - input: ```pg_file=/opt/webwork/.../sample.pg&seed=123```
    - JSON output: 

```
{ 'status': 'OK', 
  'html': '<div>Problem</div>' 
}
```

#### Check Answer / Sunsern
  - ```POST /checkanswer``` -- Check answers with PG
    - input: ```pg_file=/opt/webwork/.../sample.pg&seed=123&AnSwEr0001=42&AnSwEr0002=x```
    - JSON output: 

```json
{ 'status': 'OK', 
  'results': { 
    'AnSwEr0001' : {
      'entered_value': '42',
      'correct_value': '42',
      'is_correct': true,
      'error_msg': ''
    },
    'AnSwEr0002' : {
      'entered_value': 'x',
      'correct_value': '12',
      'is_correct': false,
      'error_msg': 'Your answer isn\'t a number'
    },
  }
}
```

Messaging API [\[sockjs_server.py\]](https://github.com/sunsern/adaptive-hint/blob/master/server/sockjs_server/sockjs_server.py)
---------------------------------------
A valid message must be in the following format:
```javascript
message = JSON.stringify({
  'message': 'some_message',
  'arguments': { 
    'arg1': 'some_text',
    'arg2': 123
  }
});
```
To send a message to the server, 
```javascript
  sock = new SockJS('http://webwork.cse.ucsd.edu:1234/student');
  ...
  sock.send(message);
```

### Student [client -> server]

  - ``signin`` Notifies the server that a student is connected. 

```javascript
{ 
  'message': 'signin'
  'arguments': {
    'student_id': 'scheaman',
    'course_id': 'demo',
    'set_id': 'sandbox',
    'problem_id': '1',
    'problem_body': '<div>...</div>'
  }
}
```
  - ``newstring`` Notifies the server that an answer box has been updated.
    - The client needs some logic to decide when to send the string. Basically: when user start 
typing in a new box. Or when some time-out occured (10sec)

```javascript
{ 
  'message': 'newstring'
  'arguments': {
    'boxname': 'AnSwEr0001',
    'value': '123'
  } 
}
```

### Student [server -> client]
  - ``hint`` Inserts a hint to the student's browser
   
```javascript
{ 
  'message': 'hint'
  'arguments': {
    'hint_html': 'AnSwEr0001',
    'location': [TBD. See notes below]
  } 
}
```

### Teacher [client -> server]
  - ``list_students`` -- List all connected students
  - ``send_hint`` -- Send a hint to a student

### Teacher [server -> client]
  - ``student_joined`` Received when a student has connected to the server.
  - ``student_left`` Receieved when a student has disconnected.
  - ``student_list`` A reponse to ``list_students``


