import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import cv2
import time
import xml.etree.ElementTree as xet
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.metrics import MeanSquaredError
from tensorflow.keras.applications import MobileNetV2, InceptionV3, InceptionResNetV2
from tensorflow.keras.layers import Dense, Dropout, Flatten, Input
from tensorflow.keras.models import Model
import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard
from SettingsLoad import settingsLoad             

class CnnLearn:

    def __init__(self):
        settings = settingsLoad()
        labels_file_path = settings.load_labels()   
        self.df = pd.read_csv(labels_file_path)
        self.data = []
        self.output = []

    def getFilename(self, filepath):
        try:
            xml_root = xet.parse(filepath).getroot()
            filename_image = xml_root.find('filename').text
            filepath_image = os.path.join('./Foto_SPZ', filename_image)
        except Exception as e:
            print(f"Error processing file {filepath}: {e}")
            filepath_image = None
        return filepath_image

    def picture_dimensions(self):
        self.df['image_path'] = self.df['filepath'].apply(self.getFilename)
        self.df.dropna(subset=['image_path'], inplace=True)

        for _, row in self.df.iterrows():
            file_path = row['image_path']
            img_arr = cv2.imread(file_path)
            if img_arr is None:
                continue
            h, w, d = img_arr.shape

            labels = row[1:5].values  
            xmin, xmax, ymin, ymax = labels
            nxmin, nxmax = xmin/w, xmax/w
            nymin, nymax = ymin/h, ymax/h
            label_norm = (nxmin, nxmax, nymin, nymax)

            load_image = load_img(file_path, target_size=(224, 224))
            load_image_arr = img_to_array(load_image)
            norm_load_image_arr = load_image_arr / 255.0

            self.data.append(norm_load_image_arr)
            self.output.append(label_norm)

        x = np.array(self.data, dtype=np.float32)
        y = np.array(self.output, dtype=np.float32)
        return x, y

    def nn_learning(self,x,y):
        x_train,x_test,y_train,y_test = train_test_split(x,y,train_size=0.8,random_state=0)

        inception_resnet = InceptionResNetV2(weights="imagenet",include_top=False,input_tensor=Input(shape=(224,224,3))) 
        inception_resnet.trainable=False  

        headmodel = inception_resnet.output
        headmodel = Flatten()(headmodel)
        headmodel = Dense(500,activation='relu')(headmodel)
        headmodel = Dense(250,activation='relu')(headmodel)
        headmodel = Dense(4,activation='sigmoid')(headmodel)  

        model = Model(inputs=inception_resnet.input,outputs=headmodel)

        model.compile(loss='mse',optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4))
        tfb = TensorBoard('object_detection')
        start_time = time.time()
        history = model.fit(x=x_train,y=y_train,batch_size=10,epochs=100,validation_data=(x_test,y_test),callbacks=[tfb])
        end_time = time.time()
        training_time = end_time - start_time

        mse = MeanSquaredError()
        mse.update_state(y_test, model.predict(x_test))
        test_mse = mse.result().numpy()
        print(f"Trénovanie neurónovej siete trvalo: {training_time} sekúnd")
        print(f"Mean Squared Error (MSE): {test_mse}")
        print(f"Úspešnosť detekcie: {((1-test_mse)*100):.2f}%")

        model.save('./My_models/object_detuction.h6')
