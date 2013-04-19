=======
pyfaceb
=======

Introduction
------------

This python library was started because most of the existing libraries
out there are either no longer in development, use the old REST API, or
are lacking in support of the more advanced features available, such as
batch querying and FQL support.

Purpose
-------

    1. to provide a lightweight, easy to use Python wrapper for the Facebook
    Graph API and Facebook Query Language (FQL) interface.

    2. to provide a nice API to Facebook's batch query interface.

    3. to make it easy to use multiple access tokens, where appropriate /
    necessary.

Basic Usage Examples
--------------------

    fbg = FBGraph('access-token')
     
    me = fbg.get('me')
     
    # prints your first name
    print me['first_name']
     
    # prints out the name of all your likes
    my_likes = fbg.get('me/likes')
    for like in my_likes['data']:
        print like['name']
     
    # make a request with parameters...
    my_first_3_likes = fbg.get('me/likes', {'limit': 3})
     
    # get an object by it's ID #:
    facebook_platform_page = fbg.get('19292868552')

Batched Query Examples
----------------------

    # batched queries with a single access token
    fbg = FBGraph('access-token')

    # you can write it manually if you like...
    results = fbg.batch([
        {'method': 'GET', 'relative_url': 'me'},
        {'method': 'GET', 'relative_url': 'me/friends?limit=50'}
    ])

    # or use the GetRequestFactory
    batch = [GetRequestFactory('me'), GetRequestFactory('me/friends', limit=50)]
    fbg.batch(batch)

    # If you need to use multiple access tokens in
    # one batch call, you can!
    # Note, you still must specify a "fallback" token when you create an
    # instance of FBGraph()
    fbg.batch([
        GetRequestFactory('PAGE1_FB_OBJ_ID', access_token=PAGE1_ACCESS_TOKEN),
        GetRequestFactory('PAGE2_FB_OBJ_ID', access_token=PAGE2_ACCESS_TOKEN),
        GetRequestFactory('PAGE3_FB_OBJ_ID', access_token=PAGE3_ACCESS_TOKEN),
    ])
   
