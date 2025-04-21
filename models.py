import sqlite3


class Schema:
   def __init__(self):
       self.conn = sqlite3.connect('translations.db')
       self.create_translation_table()

   def __del__(self):
       # body of destructor
       self.conn.commit()
       self.conn.close()

   def create_translation_table(self):

       query = """
       CREATE TABLE IF NOT EXISTS "en_es" (
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         English TEXT,
         Spanish TEXT
       );
       """

       self.conn.execute(query)

class TranslationModel:
   TABLENAME = "en_es"

   def __init__(self):
       self.conn = sqlite3.connect('translations.db')
       self.conn.row_factory = sqlite3.Row

   def __del__(self):
       # body of destructor
       self.conn.commit()
       self.conn.close()

   def get_by_id(self, id):
       where_clause = f"id = {id}"
       return self.list_items(where_clause)

   def create(self, params):
       print (params)
       query = f'insert into {self.TABLENAME} (English, Spanish)' \
               f'values ("{params.get("English")}","{params.get("Spanish")}")'
       result = self.conn.execute(query)
       return self.get_by_id(result.lastrowid)

   def delete(self, item_id):
       query = f"DELETE FROM {self.TABLENAME} " \
               f"WHERE id = {item_id}"
       print (query)
       self.conn.execute(query)
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
