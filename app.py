
from flask import Flask, render_template, request
import numpy as np
import re
from keras.models import load_model
import tensorflow as tf
import pandas as pd
import base64
from scipy.misc import imread, imresize
import json

app = Flask(__name__)

model = load_model('models/model_cnn.h5')
graph = tf.get_default_graph()



# decoding an image from base64 into raw representation
def convertImage(imgData1):
    imgstr = re.search(r'base64,(.*)', str(imgData1)).group(1)
    with open('saved_image/test_image.png', 'wb') as output:
        output.write(base64.b64decode(imgstr))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/predict/', methods=['GET', 'POST'])
def predict():

    label_data = pd.read_csv("labels_all.csv", delimiter=",")
    imgData = request.get_data()
    # encode it into a suitable format
    convertImage(imgData)

    x_test = imread('saved_image/test_image.png', mode='L')
    x_test = imresize(x_test, (32, 32))
    datas=[]
    datas.append(x_test.flatten())
    x_test = np.array(datas).reshape(-1, 32, 32, 1)
    x_test=x_test/255



    with graph.as_default():
        prediction = model.predict_classes(x_test)
        probability = model.predict_proba(x_test)

    # squeeze value from 1D array
    label = int(np.squeeze(prediction))
    label=label_data.iloc[label, :].values[0]
    max_probability = np.amax(probability)

    return json.dumps({'label':label,'probability':float(max_probability)},ensure_ascii=False)



if __name__ == "__main__":
    app.run(debug=True)

