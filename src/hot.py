
import requests 
import os 
from dotenv import load_dotenv
import time
load_dotenv()

for i in range (30):
    try:
        resp = requests.post('https://campusprinter-hotbath.sgp.appwrite.run/')
        if resp.ok:
            time.sleep(2)
            continue
        time.sleep(2)
    except Exception as e:
        pass

