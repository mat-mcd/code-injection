import json
from app import settings

class jsonhelper:

    __cache = False
    __programs_cached = {}

    @staticmethod
    def has_cache():
        return jsonhelper.__cache

    @staticmethod
    def get_pattern():
        return jsonhelper.__programs_cached

    def __init__(self):
        if settings.bits:
            #print('json 64bits initialized')
            self.json_file = open(settings.folder_assets+"/configs/programs_x64.json")
        else:
            #print('json 32bits initialized')
            self.json_file = open(settings.folder_assets+"/configs/programs_x32.json")
        try:
            self.programs_pattern = open(settings.folder_assets+"/configs/programs_cache.json")
            self.pattern_json = json.load(self.programs_pattern)
            jsonhelper.__programs_cached = self.pattern_json["programs"]
            jsonhelper.__cache = True
        except:
            pass
            #print("No cache")

        self.data = json.load(self.json_file)
        self.json_keys = []
        self.json_icons = []
        self.json_names = []
        self.json_commands = []
        self.json_status = []
        self.__get_keys()
        self.__get_names()
        self.__get_icons()
        self.__get_commands()

    def __get_keys(self):
        for key in self.data.keys():
            self.json_keys.append(key)

    def __get_names(self):
        for key in self.json_keys:
            self.json_names.append(self.data[key]["nome"])

    def __get_icons(self):
        for key in self.json_keys:
            self.json_icons.append(self.data[key]["icone"])

    def __get_commands(self):
        for key in self.json_keys:
            self.json_commands.append(settings.folder_assets+'/programs/'+self.data[key]["comando"])

    def __get_status(self):
        for key in self.json_keys:
            self.json_status.append(self.data[key]["status"])