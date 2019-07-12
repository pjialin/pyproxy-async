class ShareInstance():
    __session = None

    @classmethod
    def share(cls, **kwargs):
        if not cls.__session:
            cls.__session = cls(**kwargs)
        return cls.__session

# Expand dict
class Dict(dict):
    def get(self, key, default=None, sep='.'):
        keys = key.split(sep)
        for i, key in enumerate(keys):
            try:
                value = self[key]
                if len(keys[i + 1:]) and isinstance(value, Dict):
                    return value.get(sep.join(keys[i + 1:]), default=default, sep=sep)
                return value
            except KeyError:
                return self.dict_to_dict(default)

    def __getitem__(self, k):
        return self.dict_to_dict(super().__getitem__(k))

    @staticmethod
    def dict_to_dict(value):
        return Dict(value) if isinstance(value, dict) else value


class DataHelper:
    __origin: dict = {}
    __mappers: dict = {}

    def __init__(self, data: dict = {}, **kwargs):
        new_data = data.copy()
        new_data.update(kwargs)
        self.__generate_mappers()
        self.__origin = new_data
        for key, val in new_data.items():
            if str(key) in self.__mappers:
                self.__dict__[self.__mappers[str(key)]] = val
            elif key in self.__annotations__:
                self.__dict__[key] = val

    def __generate_mappers(self):
        for key, val in self.__annotations__.items():
            try:
                val = self.__getattribute__(key)
                if isinstance(val, str) and val.startswith('key:'):
                    tags = val.split(';')
                    self.__dict__[key] = None
                    for tag in tags:
                        tag_info = tag.split(':')
                        if tag_info[0] == 'key':
                            self.__mappers[tag_info[1]] = key
                        elif tag_info[0] == 'default':
                            self.__dict__[key] = tag_info[1]

            except (KeyError, AttributeError):
                pass

    def get_origin(self) -> dict:
        return self.__origin

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
