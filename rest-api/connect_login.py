import json
import requests
import pathlib


# login url is not correct so it is not working for now

def read_credentials(filename):
    credentials = []
    with open(filename, 'r') as file:
        for line in file:
            username, password = line.strip().split('|')  # Assuming |-separated values
            credentials.append((username, password))
    return credentials


def login(username, password):
    url = "enter-url-here/login"
    data = {"username": username, "password": password}
    response = requests.post(url, json=data)
    return response

if __name__ == "__main__":
    # username = input("Enter your username: ")
    # password = input("Enter your password: ")

    filename = '.scheduling_credentials'
    filecred = pathlib.PurePath(pathlib.Path.home(), filename)
    
    credentials = read_credentials(filecred)
    for username, password in credentials:
        print("Username:", username)
        print("Password:", password)

    response = login(username, password)
    if response.status_code == 200:
        print("Login successful!")
    else:
        print("Login failed. Status code:", response.status_code)
