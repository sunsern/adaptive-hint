// require jQuery

// Parse GET parameters from the URL
function queryObj() {
    var result = {}, keyValuePairs = location.search.slice(1).split('&');

    keyValuePairs.forEach(function(keyValuePair) {
        keyValuePair = keyValuePair.split('=');
        result[keyValuePair[0]] = keyValuePair[1] || '';
    });

    return result;
}

// Print a message to the text area for debugging
function print(msg) {
    var textbox = $("#textarea");
    textbox.val(textbox.val() + msg + "\n");
    textbox.scrollTop(
        textbox[0].scrollHeight - textbox.height()
    );
}

// Send a command to SockJS server
function send_command(sock, cmd, args) {
    sock.send(JSON.stringify({"command": cmd,
			      "arguments": args}));
    print("SENT: " + cmd + ":" + JSON.stringify(args, null, 2));
}


function create_fake_student() {
    var q = queryObj();

    // if student_id is already set, use the existing.
    if (q["student_id"]) {
	student_id = q["student_id"];
    } else {
	var randomNum = Math.ceil(Math.random()*10000);
	student_id = 'student' + randomNum;
    }
    $("#student_id").val(student_id);

    course_id = 'fake_course';
    set_id = 'fake_set';
    problem_id = '1';
}


$(document).ready(function() {
    
    create_fake_student();

    // Create a SockJS connection to the server
    sock = new SockJS("http://localhost:4350/student");

    sock.onopen = function() {
	print("INFO: connected");
	// Send `signin` command
	var params = {
	    'student_id': student_id,
	    'course_id' : course_id,
	    'set_id': set_id,
	    'problem_id': problem_id,
	    'problem_body': $("#problem-body").html()
	};
	send_command(sock, 'signin', params);
    };

    sock.onmessage = function(e) {
	print("RECIEVED: " + e.data);
    };

    sock.onclose = function() {
	print("INFO: disconnected");
    };
	
    // When a textbox loses focus, send the updated value to server.
    $("[id^=AnSwEr]").blur(function() {
	// Send 'newstring' command
	var args = { 'boxname': this.attributes["name"].value,
		     'value': this.value };
	send_command(sock, 'newstring', args);
    });

    print("INFO: document loaded");
});  
