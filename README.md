# DoubleTaskManager

Double Task Manager is a computer managment app that gives you controll over all process that run on devices in your network.

## Download
- On your server (The manager's computer) copy the direcotrys ```./all``` and ```./server```. Make sure they are both located in the smae directory!
- On your client (A computer that is being controled by your server) copy the direcotrys ```./all``` and ```./client```. Make sure they are both located in the smae directory!

## Install Dependencies
- CD into the directory where ```requirements.txt``` is located. Use the command:
  ```bash
  pip install -r requirements.txt
  ```
## Setup
- On your server, use the command ```ipconfig``` to find your IP address.
- On your clients open the ```.\all\setting.py``` file and change the IP address to match your server's address 

## Run
- On your server:
  - CD into the directory where the ```./server``` and ```./all``` dirs are located
  - In order to start your server use the command:
    ```bash
    python .\server\mainServer.py
    ```
    This will run your server and you should see the login screen

- On client side:
  - CD into the directory where the ```./client``` and ```./all``` dirs are located
  - Use the command:
    ```bash
    python .\client\mainClient.py
    ```
  
