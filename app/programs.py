from app import jsonreader
from app import settings

class programsvariables:

    __instance = None

    @staticmethod
    def get_instance():
        return programsvariables.__instance

    #Define number of programs
    def __init__(self, programs_size):
        programsvariables.__instance = self
        if(jsonreader.jsonhelper.has_cache()):
            self.programs_selected = jsonreader.jsonhelper.get_pattern()
        else:
            self.programs_selected = [0]*programs_size
        self.basic_programs = settings.code_injection['install_app']['basic']
        self.essential_programs = settings.code_injection['install_app']['essential']