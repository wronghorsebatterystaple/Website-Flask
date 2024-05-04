# Flask-Website

[Main page](https://anonymousrand.xyz)

[Blog page](https://blog.anonymousrand.xyz) (don't click this one)

Huge thanks to [Miguel Grinberg's Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) and also [Noran Saber Abdelfattah's Flask blog guide](https://medium.com/@noransaber685/building-a-flask-blog-a-step-by-step-guide-for-beginners-8bffe925cd0e), otherwise this project would've taken longer to get going and would probably have even more *bad practice* scribbled over it than it already has.

And thank you to GitHub for free image "backups" in my static folders <3

# Developer notes to compensate for possibly scuffed code

**Always check to make sure `config.py` is updated!**

**Always check to make sure access control is correct (see documentation below)!**

**Always make sure this README is updated!**

#### Access control documentation:
- Access control in view functions is achieved through the decorator `@custom_login_required(request)` decorator and the equivalent function `custom_unauthorized(request)`, provided in `app/util.py`. These are intended to replace Flask-Login's `@login_required` and `login_manager.unauthorized()` respectively.
  - On GET to banned page, these redirect to the login view as established in `config.py`, with the `next` parameter set to an absolute URL instead of `@login_required`'s relative URLs. This allows for cross-domain redirects.
  - On POST to banned pages, these return an Ajax JSON with the key `relogin=True` that makes `app/static/js/ajax_utils.js`'s `processStandardAjaxResponse()` show the login modal. This allows us to simply pop up the modal instead of redirecting away to a whole new page like `@login_required` or `login_manager.unauthorized()` would, potentially losing stuff we've put into a form (for example) in the process. In addition, returning the `relogin` key explicitly avoids the potentially bad practice of relying on CSRF token expiration and `handleCustomErrors()` in `app/templates/base.html` to detect session expiry and show the modal.
  - `@custom_login_required(request)` usage in view functions:

    ```py
    @bp.route(...)
    @custom_login_required(request)
    def view_func():
        pass
    ```

  - `custom_unauthorized(request)` usage in view functions:

    ```py
    result = util.custom_unauthorized(request)
        if result:
            return result
    ```

    - Refer to `app/admin/routes.py` and `app/blog/blogpage/routes.py` for example usages.
- `config.py` contains settings that must be up-to-date for access control:
  - `LOGIN_REQUIRED_URLS`: Flask will redirect you away from the page you are currently on if it begins with one of those URLs and you log out.
  - `VERIFIED_AUTHOR`: This is the commenter name, lowercase with no whitespace, that is restricted to admin users and will grant special comment cosmetics.
  - `PRIVATE_BLOG_IDS`: These are the blogpages hidden from the navbar in non-admin mode and that Flask will use `custom_unauthorized()` to check on attempt to access.

#### Adding new blogpages:
- Update `config.py` with proper `blog_id`, and add a developer/backrooms blogpage too with its `blog_id` being the negative of the public one
  - `blog_id` is stored and used as a string
- Update directory names in static paths if necessary

#### Adding new forms:
- All forms requiring access control must be POST and should be CSRF protected.
- Make sure that all POST forms should be Ajax using FormData and should handle the custom error(s) defined in `config.py`.
  - If JSON response from Flask has `redirect_abs_url`, it must be an absolute URL in order to be compatible with my standard Ajax response in `app/static/js/processStandardAjaxResponse()`, which can be done in Flask's `url_for()` by setting the parameter `_external=True`.
  - Refer to `app/static/js/session_util.js`, `app/admin/static/admin/js/form_submit.js`, `app/blog/static/blog/blogpage/js/comments.js`.
- Always add HTML classes `login-req-post` to `<form>`s (for handling of CSRF/session expiry in `handleCustomErrors()`) and `auth-true`/`auth-false` (for showing/hiding elements) when needed.

#### Updating HTML custom errors:
- Update `config.py`
- Update `app/routes.py` error handlers
- Update `handleCustomErrors()` in `app/templates/base.html`

#### Changing image static paths:
- Update Markdown expansion/collapse regex in `app/models.py`
- Update image paths for all existing images in db

# Blog writer notes

#### Custom Markdown syntax:
- `__[text]__` to underline
- `~~[text]~~` to strikethrough
- `\thm` and `\endthm` both surrounded by blank lines to highlight everything inside as a navy blue blockquote
- `\dropdown` and `\enddropdown` with `\summary` and `\endsummary` as the first part of the content inside, all surrounded by blank lines, to do a `<details>`-style dropdown with custom formatting
- Insert any inline tag like `<span>` with attribute `data-col-width="[something]%"` inside any table cell to control width for its column.
- Only give the filname for images in Markdown; the full path will be automatically expanded (won't work if you put in full path because I'm bad at regex!!!).

#### Other syntax notes:
- Raw HTML (including with attributes!) will be rendered, such as:
    - `<center></center>` for centering individual cells in a table
    - `<pre><code></code></pre>` for code blocks in a table
    - `<small></small>` for small text
    - `<br>` for line breaks that aren't new paragraphs and don't leave extra space, like between lines in a stanza, and `<br>` surrounded by two empty lines for more space than a normal paragraph, like between stanzas
      - `<br><br>` is also useful for when blank lines aren't tolerated or otherwise don't work, like in a footnote, table, or `\dropdown`.

#### Tables:
- Use [Markdown tables](https://www.tablesgenerator.com/markdown_tables#) whenever possible, with "Compact mode" and "Line breaks as \<br\>" checked.
- Use [reStructuredText grid tables](https://tableconvert.com/restructuredtext-generator) with "Force separate lines" checked for features such as:
  - Merged cells
    - In order to merge cells, replace intermediate '|' characters generated by the website with a space (every line has to be the same number of chars long for reStructuredText grid tables!).

# Cookie explanation from empirical observations and devtools

Comparing Flask's built-in session cookie with `PERMANENT_SESSION_LIFETIME` config vs. Flask-Login's remember me cookie with `REMEMBER_COOKIE_DURATION` config (this website currently uses the first row for no persistent cookies):

|  | Session cookie stored in: | Remember cookie stored in: | `PERMANENT_SESSION_LIFETIME` effect on session cookie | `REMEMBER_COOKIE_DURATION` effect on remember cookie | User experience when `PERMANENT_SESSION_LIFETIME` reached | User experience when `REMEMBER_COOKIE_DURATION` reached |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `session.permanent=False, remember=False` | Memory (non-persistent) | - | [Invalidated by Flask](https://stackoverflow.com/a/55055558) ([docs](https://flask.palletsprojects.com/en/3.0.x/config/#PERMANENT_SESSION_LIFETIME)) | - | Logged out | - |
| `session.permanent=True, remember=False` | Disk (persistent) | - | Expires & is deleted | - | Logged out | - |
| `session.permanent=False, remember=True` | Memory (non-persistent) | Disk (persistent) | Invalidated by Flask | Expires & is deleted | Logged out | Logged out if browser closed |
| `session.permanent=True, remember=True` | Disk (persistent) | Disk (persistent) | Expires & is deleted | Expires & is deleted | Logged out | Logged out if browser closed |

# Other useless notes

#### Rounds of Markdown processing:
  - Standard `markdown.markdown` with official extension `extra`
  - Custom Markdown extensions in `app/markdown_ext/myextensions.py`
    - Custom Markdown syntax
  - `additional_markdown_processing()` in `app/blog/blogpage/routes.py`
    - Non-custom-syntax stuff that is easier to handle from Flask than from JQuery in round 3, like regex replaces on the raw HTML output
  - JQuery in `app/static/js/display_customization.js` and `app/blog/static/blog/blogpage/js/display_customization.js`
    - Non-custom-syntax stuff that is easier to handle from JQuery, like adding classes for styling or traversing DOM

#### CSS property order (currently-used properties):
- "Specific":
  - `content`
  - `opacity`
  - `color`
    - `background-color`
  - Font:
    - `font-family`
    - `font-weight`
    - `font-style`
    - `font-size`
  - `text-decoration`
  - Other specific ones like `overflow-x`
- "General":
  - `position`
    - `top`
    - `right`
    - `bottom`
    - `left`
  - `display`
  - `width`
    - `min-width`
    - `max-width`
  - `height`
  - `border`
    - `border-width`
    - `border-style`
    - `border-color`
    - `border-radius`
  - `margin`
    - `margin-top`
    - `margin-right`
    - `margin-bottom`
    - `margin-left`
  - `padding`
    - `padding-top`
    - `padding-right`
    - `padding-bottom`
    - `padding-left`
  - `z-index`
