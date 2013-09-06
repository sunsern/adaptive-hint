adaptive-hint
=============

Requirements
------------
```
sockjs-tornado==1.0.0
tornado==3.1.1
```

Python interfaces to PG [\[server/pgwrapper.py\]](https://github.com/sunsern/adaptive-hint/blob/master/server/pgwrapper.py)
----------------------------------------------------
#### PG rendering
```python
def render_pg(pg_file, seed=1234):
    """Render a HTML snippet from a given PG file. 
    
    Args:
       pg_file : string
         Path to the PG file
       seed : int    
         Random seed
  
    Return:    
       A string containing the HTML snippet, or None if there is an error.  
                   
    Notes:       
       This function blocks until the PG generation process is complete.
       It is not recommended to call this function from the main thread.
    """
```
*Implementation details:* ``render_pg`` makes a call to a perl script ``scripts/renderPG.pl`` 
which is a variant of ``renderProblem.pl``. Once the html is generated, ``render_pg`` 
parses the html and returns only the problem part. 


#### Answer checking
```python
def checkanswer(pg_file, answers, seed=1234):
    """Check answers with a given PG file. 
	
    Args:                        
       pg_file : string
         Path to the PG file
       answers : dict                         
         Dictionary with the answers e.g. 
            { 'AnSwEr0001' : '123', 
              'AnSwEr0002' : 'x' } 
       seed : int
         Random seed

    Return:
       A dictionary containing results e.g. 
            { 'AnSwEr0001' : { 'entered_value' : '123',
                               'correct_value' : '50',
                               'is_correct' : False,
                               'error_msg' : '' },  
              'AnSwEr0002' : { 'entered_value' : 'x',
                               'correct_value' : '10',
                               'is_correct' : False,
                               'error_msg' : 'Your answer isn't a number
                               (it looks like a formula that returns a number)' } }
							   
       or None if there is an error. 

    Notes: 
       This function blocks until the answer checking process is complete.
       It is not recommended to call this function from the main thread. 
    """
```
*Implementation details:* ``checkanswer`` makes a call to a perl script ``scripts/checkanswer.pl``
that performs the following tasks.

1.  Generate a html from the PG file (same as ``renderProblem.pl``)
2.  Fill in the POST data form (i.e. answers) and submit the form to webwork server.
3.  Parse the response from the server that contains the answer results. 

Once the perl script returns, ``checkanswer`` parses the output and put the results into a python dictionary.


REST API [\[server/rest_server.py\]](https://github.com/sunsern/adaptive-hint/blob/master/server/rest_server.py)
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

Messaging API [\[server/sockjs_server.py\]](https://github.com/sunsern/adaptive-hint/blob/master/server/sockjs_server.py)
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


