class Context:
    def __init__(self):
        self.__email = None
        self.__is_authorized = False
        self.__token = None
        self.__posts = []

    @property
    def email(self):
        return self.__email

    @property
    def is_authorized(self):
        return self.__is_authorized

    @property
    def token(self):
        return self.__token

    @property
    def posts(self):
        return self.__posts

    @email.setter
    def email(self,email):
        self.__email = email

    @is_authorized.setter
    def is_authorized(self, is_authorized):
        self.__is_authorized=is_authorized

    @token.setter
    def token(self, token):
        self.__token = token

    @posts.setter
    def posts(self, posts):
        self.__posts = posts