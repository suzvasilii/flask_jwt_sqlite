class Context:
    def __init__(self):
        self.__name = None
        self.__is_authorized = False

    def get_name(self):
        return self.__name

    def get_is_authorized(self):
        return self.__is_authorized

    def set_name(self,name):
        self.__name = name

    def set_is_authorized(self, is_authorized):
        self.__is_authorized=is_authorized