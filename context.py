class Context:
    def __init__(self):
        self.__email = None
        self.__is_authorized = False
        self.__posts = []

    def get_email(self):
        return self.__email

    def get_is_authorized(self):
        return self.__is_authorized

    def get_posts(self):
        return self.__posts

    def set_email(self,email):
        self.__email = email

    def set_is_authorized(self, is_authorized):
        self.__is_authorized=is_authorized

    def set_posts(self, posts):
        self.__posts = posts