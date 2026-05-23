import mysql.connector

conexion = mysql.connector.connect(    
    user='root',    
    password='021120',
    host='localhost',    
    database='veterinaria',
    port='3306',)

print(conexion)