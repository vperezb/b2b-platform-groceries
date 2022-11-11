import flask
from flask_cors import CORS

from blueprints.admin.admin import admin_bp
from blueprints.public.public import public_bp

# App configure

app = flask.Flask(__name__)#, template_folder="templates/extensions/es_bcnmarket",  static_folder='static' )
app.secret_key = b'_5#y2L333"F4Q8z\n\xec]/'
CORS(app)

# Public views
app.register_blueprint(public_bp)
# Admin views
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8899, debug=True)
