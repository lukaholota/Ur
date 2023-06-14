from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import dotenv_values
import redis

env_vars = dotenv_values()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = env_vars['DB_URI_PROD']
app.config['REDIS_URL'] = env_vars['RDB_URI']

db = SQLAlchemy(app)
rdb = redis.Redis.from_url(env_vars['RDB_URI'])
