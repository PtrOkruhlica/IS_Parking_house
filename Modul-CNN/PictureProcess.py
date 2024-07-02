import os
import cv2
import numpy as np
from connectURL import connectURL
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt

class PictureProcess:

    def __init__(self, dir): 
        dir_actual = os.path.dirname(__file__)
        self.dir = os.path.join(dir_actual, dir)  #cesta
        self.img = None

    #
    #   nacitanie obrazku 
    #   zakazdym pripocita cislo dalsieho obrazku picture47, dalsia iteracia bude picture48 atd.
    #
    def my_load_img(self, cislo):     #,cislo
        filename = "N"
        filename += str(cislo) + '.jpeg'  
        path = os.path.join(self.dir, filename)
        self.img = cv2.imread(path) 
        print("som tu ")
        print(path)
        return self.img

        conf = confLoad()
        url = conf.conf_url()
        print("TYP URL____", type(url))
        self.img = io.imread(url)
        #self.img = io.imread('http://192.168.1.8/saved-photo')
        #cv2.imshow("obrazok", self.img)
        return self.img    
    
   