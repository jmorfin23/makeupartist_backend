from app import app



@app.route('/')
@app.route('/index')
def index():
    return "This is the make-up artist flask backend."
