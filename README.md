datatransmit
============

Client for DataAPI

Data Transmit is a python program that will poll for local relevant database
and status updates and send any changes to a DataAPI server, providing
authentication, and some interaction.

A DataAPI server is an HTTP server, which normally respond in JSON.  Details
on the DataAPI server are found at
 http://github.com/chlewey/dataapi

All JSON responses from DataAPI will include the following fields:
  api	the specific name of this DataAPI (ASCII string)
  version	the version of the DataAPI (ASCII string with dot separated
			decimal numbers)
  status	the HTTP status (integer), should be equal to the actual
			HTTP status.
  message	an accompanying message (human readable UTF-8 string) explaining
			the status.
  action	optional field, a data structure commanding to make any further
			action such as sending a particular update.
  

The Data Transmit program would send the following type of messages:

Keepalive:
  A keepalive is a GET message, authenticated per session. A keepalive message
  will be formed as:
    GET <dataapi URI>/<self>
  where the <dataapi URI> is the URI for the DataAPI server, and <self> is the
  ASCII name of the sending partner (the one that sends the keepalive).
  
  Response:
    The expected response are:
	  200	if everything is okay, no modification made (v.g. sending IP
			address = registerd IP address).
	  201	if everything is okay but a modification was made (v.g. sending IP
	        address != registered IP address).
	  401	if an authentication error happened
	  403	if sending (authenticated) partner has no access to an existing
			resource
	  404	if requested resource does not exist
			(404 takes precedence over 401 when neither requesting user or
			 resource exists)

Creation/Modification/Greeting:
  A creation message is a PUT message, alternative a POST message with the
  following format
    PUT <dataapi URI>/<self>
  where the <dataapi URI> is the URI for the DataAPI server, and <self> is the
  ASCII name of the sending partner (the one that sends the create message).
  
  The body will contain a JSON stream with the following fields:
	station	the ASCII name of the resource
	name	the full (UTF-8) name of the resource
	group	the ASCII name of the group
	passwd	optional: the password for the new resource
	user	optional: the ASCII user name of a user with modifying privileges
			in the group
	upasswd	optional: the password of the user with modifying privileges
	modify	optional: boolean indicating that the resource is meant to be
			modified
			
  As Data Transmit will only be used by a base station, the create message will
  either has the following format:
  
  When Data Transmit starts, will send a Creation/Modification with HTTP
  authentication, no passwd, user or upasswd fields, and modify field set to
  false.  This is know as a greeting message.
  
  If the program gets a 404 response for the greeting, it will ask (or take
  from the configuration file) the name and password of a privileged user
  and then send passwd, user and upasswd fields and no modify field
  (a creation message).
  
  If the program gets a 200 response with a "Send modification" action, a
  modification message should be sent.  This will include the modify field
  set to true.

  Response:
	The expected responses for a greeting are:
	  200	greeting accepted.  If a modification is required an action field
			is send in the body.
	  401	authentication failed
	  404	resource not found (creation required).
	  
	The expected responses for a modification message are:
	  201	changes accepted and committed.
	  202	message accepted and changed not committed (either because there
			is nothing to change or changes are scheduled).
	  401	authentication failed
	  403	modification will not be made, for any reason.
			(action in response might give a clue)
	  404	resource not found (creation required).

	The expected response for a creation message are:
	  201	message accepted and resource has been created
	  202	message accepted, resource has not been created yet
	  401	authentication failed for either the HTTP authentication
			or the user/upasswd pair
	  403	creation message not accepted, for any reason.
			(action in response might give a clue)

Update:
  An update message is a message containing updates for the local database and
  status.  It is a POST message and will be formed as:
    POST <dataapi URI>/<self>
  Updates are send in the request body either as JSON strings or as Sqlite3
  files.
  
  Responses:
	The expected response for an update message are:
	  200		message accepted, no modification was necessary
	  201		message accepted, modifications were made
	  202		message accepted, not all modifications have yet been committed
	  401		authentication failed (for an existing resource)
	  403		modifying resource and HTTP user do not match
	  404		resource does not exist