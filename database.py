import mysql.connector


class DB():
    def connect():
        db = mysql.connector.connect(
            host="banana.cnrmem3900ov.ap-south-1.rds.amazonaws.com",
            user="admin",
            password="20030609s",
            database="banana"
        )

        if db:
            print("connected")
        else:
            print("not connencted")

        return db
