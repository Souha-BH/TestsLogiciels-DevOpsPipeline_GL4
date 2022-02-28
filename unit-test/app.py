from multiprocessing import connection
from unittest import result
import sqlite3


def calcul_factorial(number):
    if number < 0:
        raise ValueError('calcul factorial cannot take a negative number')
    result = 1
    for i in range(1, number+1):
        result = result*i
    return result


def get_user(user_id):
    connection = sqlite3.connect("database.db")
    # {user_id, username, fullname}
    user = connection.execute(
        f"SELECT * from users WHERE user_id = {user_id}").fetchone()
    return {
        "id": user[0],
        "username": user[1],
        "fullname": user[2],

    }
