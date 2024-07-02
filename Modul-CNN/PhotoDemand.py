from SettingsLoad import settingsLoad 
from skimage import io

class photoDemand: 
    def load_photo(self): 
        sett = settingsLoad()
        server_url = sett.load_url()
        self.photo = io.imread(server_url)
        return self.photo