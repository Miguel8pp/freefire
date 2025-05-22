from flask import Flask, request, render_template, redirect, url_for, session, flash, send_file, send_from_directory, jsonify
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from pymongo import MongoClient
from bson import ObjectId
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from urllib.parse import quote_plus, urlparse, parse_qs, unquote_plus
from werkzeug.utils import secure_filename
from datetime import datetime
import os, requests, subprocess, yt_dlp, traceback, uuid, tempfile, shutil, re
from io import BytesIO
import gridfs

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'advpjsh')
bcrypt = Bcrypt(app)
socketio = SocketIO(app)

# MongoDB Atlas
username = quote_plus(os.getenv('MONGO_USERNAME'))
password = quote_plus(os.getenv('MONGO_PASSWORD'))
client = MongoClient(f"mongodb+srv://{username}:{password}@cluster0.hx8un.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['db1']
collection = db['comentarios']
comentarios_col = db['comentarios']

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/solo')
def solo():
    return render_template('solo.html')

@app.route('/duos')
def duos():
    return render_template('duos.html')

@app.route('/escuadras')
def escuadras():
    return render_template('escuadras.html')

@app.route('/diamantes')
def diamantes():
    return render_template('diamantes.html')

@app.route("/comentarios", methods=["GET", "POST"])
def comentarios():
    categorias_validas = ["general", "diamantes", "torneos"]
    categoria = request.args.get("categoria", "general")

    if categoria not in categorias_validas:
        categoria = "general"

    if request.method == "POST":
        nombre = request.form["nombre"]
        comentario = request.form["comentario"]
        estrellas = int(request.form["estrellas"])
        categoria_form = request.form.get("categoria", "general")
        if categoria_form not in categorias_validas:
            categoria_form = "general"
        
        fecha = datetime.now()
        collection.insert_one({
            "nombre": nombre,
            "comentario": comentario,
            "estrellas": estrellas,
            "fecha": fecha,
            "categoria": categoria_form,
            "reportado": False
        })
        return redirect(url_for("comentarios", categoria=categoria_form))

    comentarios = list(collection.find({
        "categoria": categoria,
        "reportado": False
    }).sort("fecha", -1))

    return render_template("comentarios.html", 
                           comentarios=comentarios, 
                           categoria=categoria,
                           categorias=categorias_validas)

@app.route("/reportar/<id>", methods=["POST"])
def reportar_comentario(id):
    from bson.objectid import ObjectId
    collection.update_one({"_id": ObjectId(id)}, {"$set": {"reportado": True}})
    return jsonify({"success": True})

if __name__ == '__main__':
    socketio.run(app, debug=True)
