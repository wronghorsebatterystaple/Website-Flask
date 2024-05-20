# can't put in config.py because current_app is not recognized when db is initialized
db_config = {
    "MAXLEN_USER_USERNAME": 25,
    "MAXLEN_USER_EMAIL": 512,
    "MAXLEN_USER_PASSWORD": 50,
    "MAXLEN_USER_PASSWORD_HASH": 256,
    "MAXLEN_COMMENT_AUTHOR": 100,
    "MAXLEN_COMMENT_CONTENT": 5000,
    "MAXLEN_POST_BLOG_ID": 5,
    "MAXLEN_POST_TITLE": 150,
    "MAXLEN_POST_SUBTITLE": 150,
    "MAXLEN_POST_CONTENT": 100000
}

