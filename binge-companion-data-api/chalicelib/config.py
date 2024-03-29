import dotenv
import os

dotenv.load_dotenv()

RDB_USER = os.environ.get('RDB_USER')
RDB_PASSWORD = os.environ.get('RDB_PASSWORD')
RDB_HOST = os.environ.get('RDB_HOST')
RDB_DATABASE_NAME = os.environ.get('RDB_DATABASE_NAME')
