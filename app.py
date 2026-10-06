import os
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

# Configuración de conexión para Local y Render (MongoDB Atlas)
mongo_uri = os.environ.get("MONGO_URI")
if not mongo_uri:
    if os.environ.get("RENDER"):
        raise RuntimeError("Configura MONGO_URI en Render.")
    mongo_uri = "mongodb://127.0.0.1:27017/"

cliente = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
base_datos = cliente["escuela_practica"]
alumnos = base_datos["alumnos"]

@app.route("/")
def inicio():
    try:
        lista_alumnos = list(alumnos.find())
        return render_template("index.html", alumnos=lista_alumnos)
    except Exception:
        return render_template("error.html", mensaje="No fue posible conectar con la base de datos. Revisa la configuración y vuelve a intentar.")

@app.route("/agregar", methods=["POST"])
def agregar():
    nombre = request.form.get("nombre", "").strip()
    grupo = request.form.get("grupo", "").strip()
    turno = request.form.get("turno", "").strip()

    if not nombre or not grupo or not turno:
        return render_template("error.html", mensaje="Todos los campos son obligatorios.")

    alumnos.insert_one({"nombre": nombre, "grupo": grupo, "turno": turno})
    return redirect(url_for("inicio"))

@app.route("/editar/<id>", methods=["GET", "POST"])
def editar(id):
    try:
        alumno = alumnos.find_one({"_id": ObjectId(id)})
        if not alumno:
            return render_template("error.html", mensaje="El alumno no existe.")
    except Exception:
        return render_template("error.html", mensaje="Identificador de alumno no válido.")

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        grupo = request.form.get("grupo", "").strip()
        turno = request.form.get("turno", "").strip()

        if not nombre or not grupo or not turno:
            return render_template("error.html", mensaje="Todos los campos son obligatorios.")

        alumnos.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"nombre": nombre, "grupo": grupo, "turno": turno}}
        )
        return redirect(url_for("inicio") + "#lista")

    return render_template("editar.html", alumno=alumno)

@app.route("/eliminar/<id>", methods=["POST"])
def eliminar(id):
    try:
        alumnos.delete_one({"_id": ObjectId(id)})
    except Exception:
        return render_template("error.html", mensaje="No se pudo eliminar el registro.")
    return redirect(url_for("inicio"))

@app.route("/ayuda")
def ayuda():
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    return render_template("ayuda.html", fecha=fecha_actual)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)