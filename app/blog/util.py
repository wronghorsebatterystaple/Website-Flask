from functools import wraps

from flask import redirect, request, url_for


def redirs_to_index_after_login():
    """
    If redirecting to this view function via the `next` parameter after logging in, instead redirect to simply the
    GET endpoint for the blog's index.
    """

    def inner_decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if request.args.get("is_redir_after_login"):
                return redirect(url_for("blog.index", _external=True))
            return func(*args, **kwargs)
        return wrapped
    return inner_decorator
