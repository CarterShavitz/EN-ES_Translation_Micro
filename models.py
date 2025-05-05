import sqlite3
import uuid
import bcrypt
import os


class Schema:
   def __init__(self):
       db_path = os.environ.get('DATABASE_PATH', 'data/translations.db')
       # Ensure the directory exists
       os.makedirs(os.path.dirname(db_path), exist_ok=True)
       self.conn = sqlite3.connect(db_path)
       self.create_translation_table()
       self.create_user_table()

   def __del__(self):
       # body of destructor
       self.conn.commit()
       self.conn.close()

   def create_translation_table(self):
        """Function to create the translation table of en_es
        """
        query = """
            CREATE TABLE IF NOT EXISTS "en_es" (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                English TEXT,
                Spanish TEXT
            );
            """

        self.conn.execute(query)

   def create_user_table(self):
        """Function to create the user table
        """
        query = """
       CREATE TABLE IF NOT EXISTS "user" (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         username TEXT UNIQUE NOT NULL,
         password_hash TEXT NOT NULL,
         api_key TEXT UNIQUE
       );
       """

        self.conn.execute(query)

class UserModel:
   """Class to establish the user model to run functions on the database
    """
   TABLENAME = "user"

   def __init__(self, conn):
       self.conn = conn
       self.conn.row_factory = sqlite3.Row

   def generate_api_key(self):
        return str(uuid.uuid4())

   def register_user(self, params):
       """Function to register the user and input the proper information and create an API Key
        """
       username = params.get("username")
       password = params.get("password")
       if username and password:
            password_bytes = password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            api_key = self.generate_api_key()
            try:
                query = f'insert into {self.TABLENAME} (username, password_hash, api_key) ' \
                        f'values ("{username}","{hashed_password}","{api_key}")'
                self.conn.execute(query)
                self.conn.commit()
                return self.get_user_by_username(username)
            except sqlite3.IntegrityError:
                return None

   def get_user_by_username(self, username):
       query = f'SELECT * FROM {self.TABLENAME} WHERE username = "{username}"'
       result = self.conn.execute(query).fetchone()
       return result

   def get_user_by_api_key(self, api_key):
        query = f'SELECT * FROM {self.TABLENAME} WHERE api_key = "{api_key}"'
        result = self.conn.execute(query).fetchone()
        return result

class TranslationModel:
   """Class to establish the translation model to run functions on the database
    """
   TABLENAME = "en_es"

   def __init__(self, conn):
       self.conn = conn
       self.conn.row_factory = sqlite3.Row

   def get_by_id(self, id):
       where_clause = f"id = {id}"
       return self.list_items(where_clause)

   def create(self, params):
       query = f'insert into {self.TABLENAME} (English, Spanish) ' \
               f'values ("{params.get("English")}","{params.get("Spanish")}")'
       result = self.conn.execute(query)
       self.conn.commit()  # Explicitly commit the transaction
       return self.get_by_id(result.lastrowid)

   def delete(self, item_id):
       query = f"DELETE FROM {self.TABLENAME} " \
               f"WHERE id = {item_id}"
       print (query)
       self.conn.execute(query)
       self.conn.commit()  # Explicitly commit the transaction
       return self.list_items()

   def update(self, item_id, update_dict):
       """
       column: value
       Name: new name
       """
       set_query = ", ".join([f'{column} = "{value}"'
                    for column, value in update_dict.items()])

       query = f"UPDATE {self.TABLENAME} " \
               f"SET {set_query} " \
               f"WHERE id = {item_id}"

       self.conn.execute(query)
       self.conn.commit()  # Explicitly commit the transaction
       return self.get_by_id(item_id)

   def list_items(self, where_clause="TRUE"):
       query = f"SELECT id, English, Spanish " \
               f"from {self.TABLENAME} " \
               f"WHERE {where_clause}"
       print (query)
       result_set = self.conn.execute(query).fetchall()
       print (result_set)
       result = [{column: row[i]
                 for i, column in enumerate(result_set[0].keys())}
                 for row in result_set]
       return result
