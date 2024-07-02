import numpy as np
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.preprocessing.image import img_to_array
import pytesseract as pt
import TextSender as dbcon
from SettingsLoad import settingsLoad              
from PIL import Image

class predictions:
    def __init__(self):
        settings = settingsLoad()
        self.models_file_path = settings.load_modelData()
        self.model = tf.keras.models.load_model(self.models_file_path)

    def tec_detection(self, photo): 
        image=photo
        image = np.array(image,dtype=np.uint8) 
        #print(image.shape)
        image1 = Image.fromarray(image).resize((224, 224))

        image_arr_224 = img_to_array(image1)/255.0 
        h,w,d = image.shape

        test_arr = image_arr_224.reshape(1,224,224,3) 

        coordinates = self.model.predict(test_arr)
 
        denorm = np.array([w,w,h,h])
        coordinates = coordinates* denorm
        coordinates = coordinates.astype(np.int32) 
        return image, coordinates

    def ecv_to_text(self,photo):    
        image, cords = self.tec_detection(photo)    
        
        img = np.array(image)

        xmin, xmax, ymin, ymax = cords[0]
        roi = img[ymin:ymax,xmin:xmax] 
        while True:  
            text = pt.image_to_string(roi)  
            if text.isalnum():
                break  
            roi = img[ymin:ymax, xmin:xmax]

        text = pt.image_to_string(roi)
        text = self.removeSpace(text)

        dbc = dbcon.textSender()
        dbc.text_send(text)

    def removeSpace(self, string):
        return string.replace(" ", "")
