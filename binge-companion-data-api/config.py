import os
import dotenv

dotenv.load_dotenv()

RDB_USER = os.environ['RDB_USER']
RDB_PASSWORD = os.environ['RDB_PASSWORD']
RDB_HOST = os.environ['RDB_HOST']
RDB_DATABASE_NAME = os.environ['RDB_DATABASE_NAME']
