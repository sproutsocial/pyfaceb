pyfaceb
=======

Introduction
------------

This python library was started because most of the existing libraries
out there (pyfacebook, facepy, facebook python-sdk) are either no longer
in development, use the old REST API, or are lacking in support of the
more advanced features available, such as batch querying and FQL
support.

Purpose
-------

A lightweight Python wrapper for the Facebook Graph API and Facebook
Query Language (FQL) interface.

Supports basic and advanced features of the Graph API, including batched
API queries, optionally with multiple access_token's.

Basic Usage Examples
--------------------

	fbg = FBGraph('insert-facebook-oauth-token-here')
	
	me = fbg.get('me')
	
	# prints your first name
	print me['first_name']
	
	# prints out the name of all your likes
	my_likes = fbg.get('me', 'likes')
	for like in my_likes['data']:
	   print like['name']
	
	# make a request with parameters...
	my_first_3_likes = fbg.get('me', 'likes', {'limit': 3})
	
	# get an object by it's ID #:
	facebook_platform_page = fbg.get('19292868552')
