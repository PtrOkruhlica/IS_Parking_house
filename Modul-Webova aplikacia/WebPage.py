from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
import MySQLdb
import _mysql_connector
import pandas as pd
import qrcode
from io import BytesIO
import os
from datetime import datetime
import time
import random
import hashlib
from flask_mail import Mail, Message
import math
import random
import string
import sys

app = Flask(__name__,template_folder='templates')
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'xxxxx'  # 
app.config['MYSQL_DB'] = 'xxxxx'
mysql = MySQL(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'xxx.xxx@gmail.com' 
app.config['MAIL_PASSWORD'] = 'xxxxx'
mail = Mail(app)

@app.route("/home")
def home():
    message = request.args.get('message', None)
    sql_querry = "SELECT 20 - COUNT(Id_vozidla) FROM `vozidlo`;"
    mycursor = mysql.connection.cursor()
    mycursor.execute(sql_querry)
    myresult_3 = mycursor.fetchall()
    return render_template('home.html',myresult_3=myresult_3, message=message)
    
@app.route("/login_admin",methods=['GET','POST']) 
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT Meno, Heslo FROM administrator WHERE Meno = '{username}'")
        user = cur.fetchone()
        print("user = ", user)
        cur.close()
        if user and password == user[1]:
            session['username'] = user[0]
            return redirect(url_for('parking_data'))
        else:
            return render_template('login_admin.html', error = 'Nesprávne meno, alebo heslo.') 
    return render_template('login_admin.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('home', message='Boli ste odhlásený.')) #

@app.route("/login_user",methods=['GET','POST']) 
def login_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()

        cur.execute(f"SELECT Meno, Heslo FROM zakaznik WHERE Meno = '{username}'")
        user = cur.fetchone()
        print("user = ", user)
        cur.close()
        if user and hashlib.sha256(password.encode()).hexdigest() == user[1]:
            session['username'] = username
            return redirect(url_for('users_data'))
        else:
            return render_template('login_user.html', error='Nesprávne meno, alebo heslo.')    
    
    return render_template('login_user.html')

@app.route("/users_data", methods=["GET", "POST"])
def users_data():
    if 'username' in session:
        username = session['username']
        mycursor = mysql.connection.cursor()

        mycursor.execute("SELECT FK_ID_Vozidla FROM Zakaznik WHERE Meno = %s", (username,))
        fk_id_vozidla = mycursor.fetchone()[0]  

        mycursor.execute("SELECT ROUND((TIMESTAMPDIFF(HOUR, Cas_prichodu, IFNULL(Cas_Odchodu, NOW()))),1) FROM Zaznamy WHERE fk_id_Vozidla = %s", (fk_id_vozidla,))
        cas_parkovania = mycursor.fetchone()[0]
        mycursor.execute("""SELECT CASE WHEN (Hodiny_zdarma - %s) < 0 THEN 0 ELSE (Hodiny_zdarma - %s) END FROM Zakaznik WHERE Meno = %s""", (cas_parkovania, cas_parkovania, username,))
        Hodiny_zdarma = mycursor.fetchone()[0]  

        mycursor.execute("SELECT Ecv_Vozidla FROM Vozidlo WHERE ID_Vozidla = %s", (fk_id_vozidla,))
        ecv_vozidla = mycursor.fetchone()[0]

        mycursor.execute("SELECT Umiestnenie FROM Zaznamy WHERE fk_id_Vozidla = %s", (fk_id_vozidla,))
        umiestnenie = mycursor.fetchone()[0]
        mycursor.execute("SELECT Cas_prichodu FROM Zaznamy WHERE fk_id_Vozidla = %s", (fk_id_vozidla,))
        cas_prichodu = mycursor.fetchone()[0]
        if(Hodiny_zdarma > 0):            
            cena = 0
        else:
            mycursor.execute("SELECT ROUND((TIMESTAMPDIFF(HOUR, Cas_prichodu, IFNULL(Cas_Odchodu, NOW()))*Tarifa_hod),1) FROM Zaznamy WHERE fk_id_Vozidla = %s", (fk_id_vozidla,))
            cena = mycursor.fetchone()[0]

        mycursor.close()
        return render_template('users_data.html',fk_id_vozidla=fk_id_vozidla, Hodiny_zdarma=Hodiny_zdarma, ecv_vozidla=ecv_vozidla,umiestnenie=umiestnenie,cas_prichodu=cas_prichodu,cena=cena )
    else:
        return redirect(url_for('login_user'))

@app.route("/payment", methods=["GET", "POST"])
def payment():
    message = None
    cursor = mysql.connection.cursor()
    
    if request.method == "POST":
        selected_plate = request.form.get("license-plate")
        try:
            cursor.execute("SELECT ID_Vozidla FROM vozidlo WHERE Ecv_Vozidla = %s", (selected_plate,))
            id_vozidla = cursor.fetchone()[0]
            print("ID_Vozidla:", id_vozidla, "| Dátový typ:", type(id_vozidla))
            cursor.execute("SELECT zakaznik.ID_Zakaznika FROM vozidlo JOIN zakaznik ON vozidlo.ID_Vozidla = zakaznik.FK_ID_Vozidla WHERE vozidlo.ID_Vozidla = %s", (id_vozidla,))
            id_zakaznika = cursor.fetchone()[0]
            print("ID_Zakaznika:", id_zakaznika, "| Dátový typ:", type(id_zakaznika))
            if id_vozidla != None:
                # Delete the row from the Vozidlo table
                cursor.execute("INSERT INTO Platba (ID_Platby, Zaplatene, FK_Id_vozidla, FK_ID_Zakaznika) VALUES (%s, %s, %s, %s)", (None,1,id_vozidla, id_zakaznika))
                cursor.execute("DELETE FROM vozidlo WHERE ID_Vozidla = %s", (id_vozidla,))
                cursor.execute("DELETE FROM zakaznik WHERE FK_ID_Vozidla = %s", (id_vozidla,))
                mysql.connection.commit()
                message = "Cena bola zaplatena"
                return redirect(url_for('home', message=message))
        except MySQLdb.Error as e:
            message = f"An error occurred: {e}"            
    cursor.execute("SELECT ID_Vozidla, Ecv_Vozidla FROM vozidlo")
    license_plates = cursor.fetchall()
    return render_template('payment.html', license_plates=license_plates, message=message)

@app.route("/get_id/<selected_plate>")
def get_id(selected_plate):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT ID_Vozidla FROM vozidlo WHERE Ecv_Vozidla = %s", (selected_plate,))
    data = cursor.fetchone()
    if data:
        return jsonify({'ID_Vozidla': data[0]})
    else:
        return jsonify({'ID_Vozidla': ''})

@app.route("/get_cas_prichodu/<id_vozidla>")
def get_cas_prichodu(id_vozidla):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Cas_prichodu FROM zaznamy WHERE fk_id_vozidla = %s", (id_vozidla,))
    data = cursor.fetchone()
    if data:
        cas_prichodu = data[0].strftime('%d.%m.%Y %H:%M:%S')
        return jsonify({'cas_prichodu': cas_prichodu})
    else:
        return jsonify({'cas_prichodu': None})

@app.route("/get_cas_odchodu/<id_vozidla>")
def get_cas_odchodu(id_vozidla):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT IFNULL(Cas_Odchodu, NOW()) FROM Zaznamy WHERE fk_id_Vozidla = %s", (id_vozidla,))
    data = cursor.fetchone()
    if data:
        cas_odchodu = data[0].strftime('%d.%m.%Y %H:%M:%S')
        return jsonify({'cas_odchodu': cas_odchodu})
    else:
        return jsonify({'cas_odchodu': None})

@app.route("/get_price/<id_vozidla>")
def get_price(id_vozidla):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT ROUND((TIMESTAMPDIFF(HOUR, Cas_prichodu, IFNULL(Cas_Odchodu, NOW()))),1) FROM Zaznamy WHERE fk_id_Vozidla = %s", (id_vozidla,))
    cas_parkovania = cursor.fetchone()[0]
    #print("cas_parkovania= ",cas_parkovania)

    cursor.execute("""SELECT (Hodiny_zdarma - %s) FROM Zakaznik WHERE fk_id_Vozidla = %s""", (cas_parkovania, id_vozidla,))
    parking_time = cursor.fetchone()[0]
    if parking_time < 0:
        price = round(abs(parking_time*0.4),1)
    else:
        price=0
    print("cena= ", price)
    cursor.close()
    return jsonify({'price': price})


@app.route("/parking_data")
def parking_data():
    if 'username' not in session:
        return redirect(url_for('login_admin'))
    else:
        sql_querry = "SELECT ID_Zaznamu,Ecv_Vozidla,Cas_prichodu,Cas_Odchodu,Tarifa_hod,Umiestnenie, ROUND((TIMESTAMPDIFF(HOUR, Cas_prichodu, IFNULL(Cas_Odchodu, NOW()))*Tarifa_hod),1),zakaznik.ID_Zakaznika FROM `zaznamy` INNER JOIN `vozidlo` ON zaznamy.fk_id_Vozidla=vozidlo.ID_Vozidla INNER JOIN `zakaznik` ON zaznamy.fk_id_zakaznika=zakaznik.ID_Zakaznika;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult = mycursor.fetchall()

        # Horny graf data
        sql_querry = "SELECT COUNT(Id_vozidla) FROM vozidlo;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_2 = mycursor.fetchall()

        sql_querry = "SELECT 20 - COUNT(Id_vozidla) FROM `vozidlo`;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_3 = mycursor.fetchall()

        #______MONDAY_____
        sql_querry="SELECT SUM(CASE WHEN DAYOFWEEK(Cas_prichodu) = 2 THEN 1 ELSE 0 END) FROM zaznamy;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_4 = mycursor.fetchall()

        #______TUESDAY_____
        sql_querry="SELECT SUM(CASE WHEN DAYOFWEEK(Cas_prichodu) = 3 THEN 1 ELSE 0 END) FROM zaznamy;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_5 = mycursor.fetchall()

        #______WEDNESDAY_____
        sql_querry="SELECT SUM(CASE WHEN DAYOFWEEK(Cas_prichodu) = 4 THEN 1 ELSE 0 END) FROM zaznamy;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_6 = mycursor.fetchall()

        #______THURSDAYSDAY_____
        sql_querry="SELECT SUM(CASE WHEN DAYOFWEEK(Cas_prichodu) = 5 THEN 1 ELSE 0 END) FROM zaznamy;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_7 = mycursor.fetchall()

        #______FRIDAY_____
        sql_querry="SELECT SUM(CASE WHEN DAYOFWEEK(Cas_prichodu) = 6 THEN 1 ELSE 0 END) FROM zaznamy;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_8 = mycursor.fetchall()

        #______SATURDAY_____
        sql_querry="SELECT SUM(CASE WHEN DAYOFWEEK(Cas_prichodu) = 7 THEN 1 ELSE 0 END) FROM zaznamy;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_9 = mycursor.fetchall()

        #______SUNDAY_____
        sql_querry="SELECT SUM(CASE WHEN DAYOFWEEK(Cas_prichodu) = 1 THEN 1 ELSE 0 END) FROM zaznamy;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(sql_querry)
        myresult_10 = mycursor.fetchall()

        query = "SELECT Umiestnenie FROM zaznamy INNER JOIN vozidlo ON zaznamy.fk_id_Vozidla=vozidlo.ID_Vozidla;"
        mycursor = mysql.connection.cursor()
        mycursor.execute(query)
        umiestnenie_values = [row[0] for row in mycursor.fetchall()]

    return render_template('parking_data.html',parking_data = myresult, mojeData = myresult_2, mojeData_2 = myresult_3, monday = myresult_4,tuesday = myresult_5,
                           wednesday=myresult_6,thursday=myresult_7,friday=myresult_8,saturday=myresult_9,sunday=myresult_10,umiestnenie_values=umiestnenie_values)

@app.route("/add_Vehicle", methods=["GET", "POST"])
def add_Vehicle():
    if 'username' not in session:
        return redirect(url_for('login_admin'))
    else:
        tarifa = 0.40
        current_time = datetime.now()
        if request.method == "POST":
            ecv = request.form.get("ecv")
            user_email = request.form.get("email")
            umiestnenie = request.form.get("umiestnenie")
            
            mycursor = mysql.connection.cursor()
            mycursor.execute("SELECT * FROM Vozidlo WHERE Ecv_Vozidla = %s", (ecv,))
            vehicle = mycursor.fetchone()
            if vehicle != None:
                flash('EČV sa už nachádza v systéme.', 'error')
                return render_template('add_Vehicle.html')

            query = "INSERT INTO vozidlo (ID_Vozidla, Ecv_Vozidla) VALUES (%s, %s)"
            mycursor = mysql.connection.cursor()
            mycursor.execute(query, (None, ecv))

            query_select_V = "SELECT ID_Vozidla FROM Vozidlo"
            mycursor = mysql.connection.cursor()
            mycursor.execute(query_select_V)
            fk_id_voz = mycursor.lastrowid

            name, password = generate_credentials()
            hashed_name = hashlib.sha256(name.encode()).hexdigest()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            sql = "INSERT INTO zakaznik (ID_Zakaznika,FK_ID_Vozidla,Meno,Heslo,Email,Registrovany,Hodiny_zdarma) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            val_zakaznik = (None,fk_id_voz,hashed_name,hashed_password,user_email,True,100) 
            mycursor.execute(sql, val_zakaznik)

            query_select_Z = "SELECT ID_Zakaznika FROM Zakaznik"
            mycursor = mysql.connection.cursor()
            mycursor.execute(query_select_Z)
            fk_id_zakaznika = mycursor.lastrowid

            query = "INSERT INTO zaznamy (ID_Zaznamu,Cas_prichodu,Cas_Odchodu,Tarifa_hod,Umiestnenie,fk_id_Vozidla,fk_id_zakaznika) VALUES (%s,%s,%s,%s,%s,%s,%s)"
            mycursor = mysql.connection.cursor()
            val_zaznam = (None,current_time,None,tarifa,umiestnenie,fk_id_voz,fk_id_zakaznika) 
            mycursor.execute(query, val_zaznam)
            mysql.connection.commit()
            try:
                send_email(user_email, name, password)  
                message = user_email
            except Exception as e:
                message = str(e)
            return redirect(url_for('parking_data',message=message))
        else:
            query = "SELECT Umiestnenie FROM zaznamy INNER JOIN vozidlo ON zaznamy.fk_id_Vozidla=vozidlo.ID_Vozidla;"
            mycursor = mysql.connection.cursor()
            mycursor.execute(query)
            existing_values = [record[0] for record in mycursor.fetchall()]
            #generovanie hodnoty pre umiestnenie
            new_value = random.choice([i for i in range(1, 21) if i not in existing_values])
        return render_template('add_Vehicle.html', new_value=new_value)



def send_email(to, name, password):
    msg = Message('Vaše prihlasovacie údaje do parkovacieho systému', recipients=[to])
    msg.body = f'\nVaše prihlasovacie meno: {name}\n a heslo: {password}\n'
    try:
        mail.send(msg)
        print("Email bol odoslaný")
    except Exception as e:
        print(f"Email sa nepodarilo odoslať: {e}")


def random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    str = ''
    for i in range(length):
        str += random.choice(letters_and_digits)
    return str

def generate_credentials(self):
    name = self.random_string(8)
    password = self.random_string(10)
    return name, password

if __name__ == "__main__":
    app.run(debug=True)
    