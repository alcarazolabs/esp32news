# WebService App
from flask import Flask
from flask import jsonify
from flask_cors import CORS, cross_origin
from flask_marshmallow import Marshmallow
import pytz
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from config import DATABASE_CONNECTION_URI

app = Flask(__name__)

# ser cors
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# set a key to be able of show messages with flash
app.config['SECRET_KEY'] = '123456'

# set a custom variable to access from template
app.config['PROJECT_HOST'] = 'http://localhost:5000'

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_CONNECTION_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class News(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    news = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, news, created_at):
        self.news = news
        self.created_at = created_at

class NewsSchema(ma.Schema):
    class Meta:
        fields = ('id', 'news', 'created_at')

news_schema = NewsSchema()
news_schema = NewsSchema(many=True)

def getFechaActual():
    ist = pytz.timezone('America/Lima')
    datetime_ist = datetime.now(ist)
    fecha_actual = datetime_ist.strftime('%Y-%m-%d %H:%M:%S')

    return fecha_actual

@app.route('/news', methods=['GET'])
@cross_origin() # allow cors
def get_news():

    news = News.query.order_by(News.id.desc()).limit(1)
    result = news_schema.dump(news)

    return jsonify(result)


if __name__ == "__main__":
    #app.run(port=5000, debug=False) # Only use this for local deployement
    #app.run() # Only usi this for heroku deploy
	# use the next code for docker image deploy:
	#port = int(os.environ.get('PORT', 5000))
	app.run(host='192.168.18.42', port=5000)