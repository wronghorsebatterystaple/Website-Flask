from app import app # import app variable from app package

@app.route("/")
def index():
    return "Hello, World!"
