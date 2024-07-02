import mysql.connector
import datetime
import random
import string
import hashlib

class textSender:

    def __init__(self):
        pass

    def id_generate(self):
        number = 1
        while number<2:
            number += 1
        return number
    
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


    def car_lot(self):
        connection = mysql.connector.connect(host="localhost",user="root",password="XXXX",database="parking_house")
        mycursor = connection.cursor()
        query = "SELECT Umiestnenie FROM zaznamy INNER JOIN vozidlo ON zaznamy.fk_id_Vozidla=vozidlo.ID_Vozidla;"
        mycursor.execute(query)
        occupied_pos = []
        available_pos= []
        result = mycursor.fetchall()
        for i in result:
            occupied_pos.append(i[0])

        if len(occupied_pos) == 20:
            return "Parkovací dom má vyčerpané voľné parkovacie kapacity"
        else:
            for i in range(1, 21):
                if i not in occupied_pos:
                    available_pos.append(i)
            generated_pos = random.choice(available_pos)
            return generated_pos


    def text_send(self, text):    
        # connecting to Mysql database
        connection = mysql.connector.connect(host="localhost",user="root",password="XXXX",database="parking_house")
        if connection.is_connected():
            print("Succesfully connected")
        else:
            print("Failed to connect")
            connection.closed()    

        try:
            with connection.cursor() as cursor:
                sql = "INSERT INTO vozidlo (ID_Vozidla,Ecv_Vozidla) VALUES (%s,%s)"
                val_vozidlo = (None,text) 
                cursor.execute(sql, val_vozidlo)   
                fk_id_voz = cursor.lastrowid              
                #print("ID_Vozidla=",fk_id_voz)
                
                # SQL INSERT ZAKAZNIK
                name, password = self.generate_credentials()
                hashed_name = hashlib.sha256(name.encode()).hexdigest()
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                sql = "INSERT INTO zakaznik (ID_Zakaznika,FK_ID_Vozidla,Meno,Heslo, Email, Registrovany, Hodiny_zdarma) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                val_zakaznik = (None,fk_id_voz,hashed_name,hashed_password,None,0,None) 
                cursor.execute(sql, val_zakaznik)
                fk_id_zakaznika = cursor.lastrowid              
                print("ID_Zakaznika=",fk_id_zakaznika)

                # SQL INSERT ZAZNAM               
                current_time = datetime.datetime.now()
                car_lot = self.car_lot()      
                print("car lot = ", car_lot) 
                tarifa = 0.40
                sql = "INSERT INTO zaznamy (ID_Zaznamu,Cas_prichodu,Cas_Odchodu,Tarifa_hod,Umiestnenie,fk_id_Vozidla,fk_id_zakaznika) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                val_zaznam = (None,current_time,None,tarifa,car_lot,fk_id_voz,fk_id_zakaznika) 
                cursor.execute(sql, val_zaznam)

                # SQL INSERT Platba              
                sql = "INSERT INTO platba (ID_Platby,Zaplatene,FK_ID_Vozidla,FK_ID_Zakaznika) VALUES (%s,%s,%s,%s)"
                val_platba = (None,"",fk_id_voz,fk_id_zakaznika) 
                cursor.execute(sql, val_platba)
                connection.commit()
                print("Record inserted successfully")
        finally:
            print("Som vo finally")
            #connection.closed()      

