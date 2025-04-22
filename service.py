from models import TranslationModel, UserModel


class TranslationService:
   """Class to create a translation model and enact the correct functions
    """
   def __init__(self, conn):
       self.model = TranslationModel(conn)

   def create(self, params):
       return self.model.create(params)

   def update(self, item_id, params):
       return self.model.update(item_id, params)

   def delete(self, item_id):
       return self.model.delete(item_id)

   def list(self):
       response = self.model.list_items()
       return response
  
   def get_by_id(self, item_id):
       response = self.model.get_by_id(item_id)
       return response

class UserService:
   """Class to create a user model and enact the correct functions
    """
   def __init__(self, conn):
       self.model = UserModel(conn)

   def create_user(self, params):
       return self.model.create_user(params)
   
   def register_user(self, params):
        return self.model.register_user(params)

   def get_user_by_api_key(self, api_key):
        return self.model.get_user_by_api_key(api_key)
   