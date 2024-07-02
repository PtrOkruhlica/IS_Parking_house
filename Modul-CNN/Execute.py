
from Predictions import predictions
import TextSender as txtSend 
from CnnLearn import CnnLearn
from PhotoDemand import photoDemand

class execute:
        
    def __init__(self):
      self.photo = photoDemand()

    def executing(self):
        
      # Odkomentovat pre trenovanie neuronovej siete 
      # a cyklus WHILE zakomentovat cely
      
      #learning = CnnLearn()
      #learning.nn_learning()

      while True:
          photo = self.photo.load_photo()
          predict = predictions()
          text = predict.ecv_to_text(photo)
          dbc = txtSend.textSender()
          dbc.text_send(text)

        