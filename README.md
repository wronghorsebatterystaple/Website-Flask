# Flask-Website

[Main page](https://anonymousrand.xyz)

[Blog page](https://blog.anonymousrand.xyz) (don't click this one)

# Setup if it's ever needed

I hope I'm not reading this because I bricked a machine again.

1. Set up things like MySql and Docker and Nginx on host machine
    * MySql data directory should be in the bind-mounted directory specified in [docker/compose.yaml](docker/compose.yaml)
    * Make sure default key for SSH and for GitHub pushing has no passcode if planning to use automatic db/image backup scripts. No hack pls
2. `git clone`
3. Add back gitignored files:
    * [docker/flask/envs/.env](docker/flask/envs/.env): randomly generated `SECRET_KEY` and pymysql `DATABASE_URL` (search private notes for reference)
    * [docker/mysql/envs/.mysqlenv](docker/mysql/envs/.mysqlenv): nothing yet (no environment variables if bind-mounting existing `/var/lib/mysql/`)
    * [backup-scripts/db_backup_config.sh](backup-scripts/db_backup_config.sh): set the variables referenced in `db_backup.sh`
4. Navigate to [docker/](docker/) and run `deploy.sh` (or use a `systemd` service)
5. For development purposes, create a Python virtualenv in the repo's folder

# Developer notes to compensate for possibly scuffed code

### IMPORTANT:
- Always make sure [.gitignore](.gitignore) is up to date with the correct paths and items! If using automatic image backups to Git, always preemptively add new files to [.gitignore](.gitignore) to avoid badly-timed auto-commits!
- Always make sure access control is correct (see documentation below)!
- Always make sure [config.py](config.py) is updated and has the correct filename/path (some Python files import it directly as a module)!
- Always make sure backup scripts in [backup-scripts/](backup-scripts/) have the correct paths and configs!
- Always make sure this README is updated!
- Always make sure Cloudflare firewall rules etc. still use the right URLs!

### Docker maintenance:
- Always make sure [docker/compose.yaml](docker/compose.yaml) is synced/updated as per comments
- Always make sure Dockerfiles and entrypoint scripts and environment variables are up to date (especially the relative paths: Dockerfile host paths are relative to Docker Compose's `context`)

### Access control documentation:
- Access control in view functions is achieved through the `@custom_login_required(request)` decorator and its equivalent function `custom_unauthorized(request)`, both provided in [app/util.py](app/util.py). These are intended to replace Flask-Login's `@login_required` and `login_manager.unauthorized()` respectively.
  - On GET to a restricted page, this function redirects to the login view as established in [config.py](config.py), with the `next` parameter set to an absolute URL instead of `@login_required`'s relative URLs. This allows for cross-domain redirects.
  - On POST to a restricted page, this function returns a JSON with the key `relogin=True` that makes [app/static/js/ajax_utils.js](app/static/js/ajax_utils.js)'s `doBaseAjaxResponse()` show the login modal. This allows us to simply pop up the modal instead of redirecting away to a whole new page like `@login_required` or `login_manager.unauthorized()` would, potentially losing stuff we've put into a form (for example) in the process. In addition, returning the `relogin` key explicitly avoids the potentially bad practice of relying on CSRF token expiration and `fetchWrapper()`'s error handling in [app/static/js/ajax_util.js](app/static/js/ajax_util.js) to detect session expiry and show the modal.
  - `@custom_login_required(request)` usage in view functions:

    ```py
    @bp.route(...)
    @util.custom_login_required(request)
    def view_func():
        pass
    ```

  - `custom_unauthorized(request)` usage in view functions:

    ```py
    result = util.custom_unauthorized(request)
    if result:
        return result
    ```

  - Refer to [app/admin/routes.py](app/admin/routes.py) and [app/blog/blogpage/routes.py](app/blog/blogpage/routes.py) for example usages
- [config.py](config.py) contains settings that must be up-to-date for access control:
  - `LOGIN_REQUIRED_URLS`: Flask will redirect you away from the page you are currently on if it begins with one of these URLs and you log out
  - `VERIFIED_AUTHOR`: This is the commenter name, lowercase with no whitespace, that is restricted to admin users and will grant special comment cosmetics (and a **real** verified checkmark!!!)
- Each blogpage in the database has a boolean `login_required` column that must be up-to-date; Flask uses this to check login redirection on attempt to access these blogpages

### CSP documentation:
- Refer to [config.py](config.py) for CSP; should be commented!

### XSS sanitization documentation:
- Comments:
  - Python's [bleach](https://pypi.org/project/bleach/) is the main library used for XSS sanitization during Markdown to HTML rendering for comments (`sanitize_comment_html()` in [app/blog/blogpage/routes.py](app/blog/blogpage/routes.py))
    - Yes it's deprecated, but there is no good alternative atm, and both bleach and its main dependency html5lib are still being maintained
    - Links and images are not allowed; full list of allowed tags is in the code linked above
- `flash` query string parameter:
  - Only JQuery's `text()` is used to insert contents into flash element, which is XSS-safe
- Other query string parameters:
  - Handled on the backend by Flask and never put directly into the DOM
- Overall:
  - CSP prevents inline scripts as a final safety measure
  - Inline styles are unfortunately still allowed because I could not figure out how to get MathJax to work without them

### Adding new blogpages:
- Add to database (reference current database entries)
  - Add a developer/backrooms blogpage too with its `blogpage_id` being the negative of the public one
  - `blogpage_id` is always an integer except for the commented cases in [config.py](config.py), where they must be strings to avoid confusion with negative values and list/dictionary accessing
- Update [config.py](config.py):
  - Update `BLOGPAGE_ID_TO_PATH` with the same paths that you gave the new blogpage and its developer blogpage in the database; this is used for blueprint initialization (we can't access database before app context is fully created)
  - Update `LOGIN_REQUIRED_URLS` with the backrooms blogpage
- Create new static directories for it in [app/blog/static/blog/blogpage/](app/blog/static/blog/blogpage/) from the [template](app/blog/static/blog/blogpage/blogpage_template/), and update other static directory names if necessary
  - Remember that since HTML templates are the same for every blogpage, things like font or background image customizations must be done through static files like CSS, which are imported individually per blogpage

### Changing blogpage IDs/blogpage static paths:
- Change the static directories, obviously
- Update paths in [config.py](config.py)
- Update Markdown expansion/collapse regex in [app/models.py](app/models.py)
- Update image paths in [app/admin/routes.py](app/admin/routes.py). This is important to make sure we don't accidentally delete/move important files!
- Update static paths for all linked JS/CSS in templates
- Update image paths for all existing images in db

### Adding new forms:
- GET forms:
  - These should not modify server-side state!
  - Usage guidelines:
    - Do not implement a CSRF Token hidden field to avoid leaking token in the URL (per OWASP guidelines). This means that we shouldn't use the `boostrap_wtf.quick_form()` macro for GET forms!
  - Refer to [app/blog/static/blog/blogpage/js/goto_page_form.js](app/blog/static/blog/blogpage/js/goto_page_form.js) and its associated [app/blog/templates/blog/blogpage/index.html](app/blog/templates/blog/blogpage/index.html) for an example of a GET form
- POST forms:
  - All other forms
  - Usage guidelines:
    - Must be Ajax, using `fetchWrapper()` in [app/static/js/ajax_util.js](app/static/js/ajax_util.js) and sending FormData (since the CSRF error handling is designed only for FormData)
  - Refer to [app/static/js/session_util.js](app/static/js/session_util.js), [app/admin/static/admin/js/form_submit.js](app/admin/static/admin/js/form_submit.js), and [app/blog/static/blog/blogpage/js/comments.js](app/blog/static/blog/blogpage/js/comments.js) for examples of POST forms
- Always add HTML classes `auth-true`/`auth-false` (for showing/hiding elements) when needed

### Updating HTML custom errors:
- Update [config.py](config.py)
- Update [app/routes.py](app/routes.py) error handlers if necessary
- Update `fetchWrapper()` in [app/static/js/ajax_util.js](app/static/js/ajax_util.js)

### Other notes:
- MySQL does not change ids (primary keys) on row delete; this is used to our advantage by having a `blog.post_by_id` view function serving permanent id-based links to posts. Keep this is mind if planning to change databases in the future.
- `url_for()` to a blueprint (trusted destination!) should always be used with `_external=True` in both HTML templates and Flask to simplify the cross-origin nature of having a blog subdomain.

# Blog writer notes

### Custom Markdown syntax:
- Inline:
  - `__[text]__` to underline
  - `~~[text]~~` to strikethrough
  - `'''[text]'''` to do code in gray 
- Blocks (all delimiters must be surrounded by one blank line). Nesting may cause unexpected consequences such as incorrect parsing or 500 error!:
  - `\dropdown` and `\enddropdown` with `\summary` and `\endsummary` as the first part of the content inside to do a `<details>`-style dropdown with custom formatting
  - `\textbox` and `\endtextbox` to put everything inside a 1-cell table
  - `\thm` and `\endthm` to highlight everything inside as a navy blue blockquote, such as for important theorems or simply matching blockquote color to code
- Images:
  - Insert `<span data-width="[number]%"></span>` around the alt text portion (within the square brackets) of images to customize image width (default 100%; accepted units: %)
  - Insert `<span data-inline></span> around the alt text portion of images to make it inline with no extra top/bottom margins. If both `data-width` and `data-inline` are present, `data-width` must be first.
  - Only give the filename for images in Markdown; the full path will be automatically expanded (won't work if you put in full path because I'm bad at regex!!!)
- Links:
  - Insert `<span data-same-page></span>` around the display text portion (within the square brackets) of links to override the default of opening them in a new tab. Note that URL fragment links (starting with '#') are automatically opened in the same page.
- Tables:
  - Insert any inline tag like `<span>` with attribute `data-col-width="[something]"` inside any table cell to control width for its column (accepted units: all). Use this to force word wrapping in tables too, otherwise they default to scrolling horizontally if too wide (note that `<pre>` cannot be wrapped).
  - Insert any inline tag like `<span>` with attributes `data-align-[center/right/top/bottom]` inside any table cell to control its non-default vertical and horizontal alignment

### Other syntax notes:
- Raw HTML (including with attributes!) will be rendered, which is useful for additional styling or in environments where Markdown equivalents may not always work (footnotes, tables, blockquotes etc.). Examples:
    - `<span></span>` with pretty much any custom CSS styling you want (or with existing styling classes, once CSP is able to block inline `style` attributes)
    - `<pre><code></code></pre>` for multiline code blocks in a table
    - `<small></small>` for small text
    - `<p></p>` for paragraphs and line breaks (note: not supported in footnotes; use `<br><br>` instead)
      - E.g. lists, which have had the space between it and the previous paragraph removed by default
    - `<br>` for line breaks that aren't new paragraphs and don't leave extra space, like between lines in a stanza, and `<br>` surrounded by two empty lines for more space than a normal paragraph, like between stanzas
- Emojis will probably not work, so use HTML character entities instead

### Tables:
- Use [Markdown tables](https://www.tablesgenerator.com/markdown_tables#) whenever possible, with "Compact mode" and "Line breaks as \<br\>" checked.
- Use [reStructuredText grid tables](https://tableconvert.com/restructuredtext-generator) with "Force separate lines" checked for features such as:
  - Merged cells
    - In order to merge cells, replace intermediate '|' characters generated by the website with a space (every line has to be the same number of chars long for reStructuredText grid tables!)
  - First row non-bolded

# Cookie explanation from empirical observations and devtools

Comparing Flask's built-in session cookie with `PERMANENT_SESSION_LIFETIME` config vs. Flask-Login's remember me cookie with `REMEMBER_COOKIE_DURATION` config (this website currently uses the first row for no persistent cookies):

|  | Session cookie stored in: | Remember cookie stored in: | `PERMANENT_SESSION_LIFETIME` effect on session cookie | `REMEMBER_COOKIE_DURATION` effect on remember cookie | User experience when `PERMANENT_SESSION_LIFETIME` reached | User experience when `REMEMBER_COOKIE_DURATION` reached |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `session.permanent=False, remember=False` | Memory (non-persistent) | - | [Invalidated by Flask](https://stackoverflow.com/a/55055558) ([docs](https://flask.palletsprojects.com/en/3.0.x/config/#PERMANENT_SESSION_LIFETIME)) | - | Logged out | - |
| `session.permanent=True, remember=False` | Disk (persistent) | - | Expires & is deleted | - | Logged out | - |
| `session.permanent=False, remember=True` | Memory (non-persistent) | Disk (persistent) | Invalidated by Flask | Expires & is deleted | Logged out | Logged out if browser closed |
| `session.permanent=True, remember=True` | Disk (persistent) | Disk (persistent) | Expires & is deleted | Expires & is deleted | Logged out | Logged out if browser closed |

# Other useless notes

### Rounds of Markdown processing:
  - Standard Python-Markdown `markdown.markdown()` with official extension `extra`
  - Custom Markdown extensions in [app/markdown_ext/myextensions.py](app/markdown_ext/myextensions.py)
    - Custom Markdown syntax
  - Custom `additional_markdown_processing()` in [app/blog/blogpage/routes.py](app/blog/blogpage/routes.py)
    - Non-custom-syntax stuff that is easier to handle from Flask than from JQuery in round 3, like regex replaces on the raw HTML
  - Custom JQuery in [app/static/js/display_customization.js](app/static/js/display_customization.js) and [app/blog/static/blog/blogpage/js/display_customization.js](app/blog/static/blog/blogpage/js/display_customization.js)
    - Non-custom-syntax stuff that is easier to handle from JQuery, like adding classes for styling or traversing DOM

### CSS property order (currently-used properties):
- Custom variables:
  - Mine
  - Bootstrap's
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
  - `background-image`
    - `background-attachment`
    - `background-position`
    - `background-repeat`
    - `background-size`
  - `overflow-wrap`
  - `text-decoration`
  - Other specific ones like `overflow-x` in alphabetical order
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
    - `min-height`
    - `max-height`
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
- Browser-specific display stuff
