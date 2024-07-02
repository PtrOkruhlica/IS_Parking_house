
from configparser import ConfigParser

class settingsLoad: 
    def load_labels(self): 
        file = 'settings.ini'
        config = ConfigParser()
        config.read(file)
        config.sections()
        path_labels = config['Settings_labels']['labels']
        return path_labels 

    def load_modelData(self):
        file = 'settings.ini'
        config = ConfigParser()
        config.read(file)
        config.sections()
        path_model = config['Settings_modelData']['model']
        return path_model

    def load_url(self):
        file = 'settings.ini'
        config = ConfigParser()
        config.read(file)
        config.sections()
        server_url = config['Settings_server']['url']
        return server_url
    
    def load_values(self):
        file = 'settings.ini'
        config = ConfigParser()
        config.read(file)
        config.sections()
        tarifa = config['Settings_values']['tarifa']
        return int(tarifa)
