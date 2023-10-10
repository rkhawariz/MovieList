import os
from os.path import join, dirname
from dotenv import load_dotenv

from http import client
from flask import Flask, render_template, request, jsonify
import certifi
ca = certifi.where()
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI, tlsCAFile=ca)

db = client[DB_NAME]

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/movie", methods=["POST"])
# membuat function movie_post yang nantinya akan berjalan saat route'/movie' pada saat client mengklik tombol save yang memiliki function posting()
def movie_post(): 
    # membuat variable untuk menampung data dari variable url_give dll yang terdapat pada index.html yang diinput oleh client
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    # variable untuk menampung data tertentu dari sebuah website yang linknya sudah diinput oleh user/client dan ditampung oleh variable url_receive 
    og_image = soup.select_one('meta[property="og:image"]')
    og_title = soup.select_one('title').text
    og_description = soup.select_one('meta[name="description"]')

    image = og_image['content']
    title = og_title
    desc = og_description['content']
    # variable untuk menyusun dictionary dengan key dan value variable yang berisi data yang sudah ditampung sebelumnya
    doc = {
        'image': image,
        'title': title,
        'description': desc,
        'star': star_receive,
        'comment': comment_receive,
    }
    # memasukan data dari variable doc ke dalam database dbSparta, collection moviesProject
    db.moviesProject.insert_one(doc)
    return jsonify({'msg':'POST request!'})

@app.route("/movie", methods=["GET"])
# function untuk mengambil data dari database
def movie_get():
    # mengambil seluruh data dalam collection kecuali key '_id'
    movie_list = list(db.moviesProject.find({},{'_id': False}))
    # data dari database yang ditampung dalam variable movie_list, ditempatkan pada Object 'movie' json, yang nantinya Object tersebut akan diambil isinya oleh function listing() pada HTML
    return jsonify({'movies':movie_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)