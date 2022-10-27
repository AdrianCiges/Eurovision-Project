# pip install selenium
# pip install webdriver_manager
# pip install catboost
# pip install beautifulsoup4
# pip install requests
# pip install websockets
# pip install -U scikit-learn
# pip3 install openpyxl
# !pip install pytube

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains as AC
from selenium.webdriver.common.keys import Keys
import random
import warnings
import time
import statistics as stats
from operator import itemgetter

warnings.filterwarnings("ignore")
from sklearn.metrics import mean_squared_error as mse
from sklearn.metrics import r2_score as r2
import pandas as pd
from catboost import CatBoostRegressor as CTR
from sklearn.model_selection import train_test_split as tts
from joblib import Parallel, delayed
import requests as req
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import asyncio
import websockets
import json
from pytube import YouTube
import os


# driver configuration
opciones = Options()
opciones.add_experimental_option("excludeSwitches", ["enable-automation"])
opciones.add_experimental_option("useAutomationExtension", False)
opciones.headless = False  # si True, no aperece la ventana (headless=no visible)
opciones.add_argument("--start-maximized")  # comienza maximizado
opciones.add_argument("user-data-dir=selenium")  # mantiene las cookies
# opciones.add_extension('driver_folder/adblock.crx')       # adblocker
# opciones.add_argument('--incognito')


PATH = ChromeDriverManager().install()
# driver=webdriver.Chrome(PATH) # Defino el Driver


# CARGAMOS DATA TO TRAIN
data = pd.read_excel("./Excels/Data_to_train.xlsx")
data.drop("Unnamed: 0", axis=1, inplace=True)

# PARTIMOS DATA
X = data.drop("propo_puntos", axis=1)
y = data.propo_puntos
X_train, X_test, y_train, y_test = tts(
    X, y, train_size=0.99, test_size=0.01, random_state=22
)
X_train.shape, X_test.shape, y_train.shape, y_test.shape

# ENTRENAMOS
ctr = CTR(iterations=5, verbose=False)
ctr.fit(X_train, y_train)
y_pred = ctr.predict(X_test)


def row_data(user_songs):
    tablas_songs = Parallel(n_jobs=6, verbose=True)(
        delayed(get_songs)(d) for d in user_songs
    )

    tabla0 = pd.DataFrame()
    tabla0 = pd.concat(tablas_songs, axis=0)

    return tabla0

def get_songs(cancion):
    
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
    }
    label_codes = {
        "Albania": 0,
        "Andorra": 1,
        "Armenia": 2,
        "Australia": 3,
        "Austria": 4,
        "Azerbaijan": 5,
        "Belarus": 6,
        "Belgium": 7,
        "Bosnia and Herzegovina": 8,
        "Bulgaria": 9,
        "Croatia": 10,
        "Cyprus": 11,
        "Czech Republic": 12,
        "Denmark": 13,
        "Estonia": 14,
        "Finland": 15,
        "France": 16,
        "Georgia": 17,
        "Germany": 18,
        "Greece": 19,
        "Hungary": 20,
        "Iceland": 21,
        "Ireland": 22,
        "Israel": 23,
        "Italy": 24,
        "Latvia": 25,
        "Lithuania": 26,
        "Malta": 27,
        "Moldova": 28,
        "Monaco": 29,
        "Montenegro": 30,
        "North Macedonia": 31,
        "Norway": 32,
        "Poland": 33,
        "Portugal": 34,
        "Romania": 35,
        "Russia": 36,
        "San Marino": 37,
        "Serbia": 38,
        "Serbia and Montenegro": 39,
        "Slovakia": 40,
        "Slovenia": 41,
        "Spain": 42,
        "Sweden": 43,
        "Switzerland": 44,
        "The Netherlands": 45,
        "Turkey": 46,
        "Ukraine": 47,
        "United Kingdom": 48 }
    song = []
    pais = []
    views = []
    likes = []
    shazams = []

    try:
        print(f"Escrapeando {cancion} en YouTube")
        url = (
            "https://www.youtube.com/results?search_query=" + cancion["song"] +
            "+" + cancion["singer"] + "+official"
        )
        link_video = 'https://www.youtube.com/watch?v=' + (req.get(f"{url}")
            .text).split('/watch?v=')[1].split(',')[0].replace('"', "")
        html = req.get(link_video, headers = {
            "Accept-Language": "es-ES,es;q=0.9"
        }).text
        video_likes = int(
            html.split(" Me gusta")[0]
            .split(":")[-1]
            .replace('"', "")
            .replace(".", "")
        )
        video_views = int(
            (bs(html)).select_one('meta[itemprop="interactionCount"][content]')[
                "content"
            ]
        )
        song.append(
            cancion["song"] + " " + cancion["singer"]
        )# Añado la canción(just to see, después dropearé)
        pais.append(
            label_codes[cancion["country"]]
        )# Añado el label del país según mi dictio
        time.sleep(random.randint(5, 7))
        views.append(video_views)
        likes.append(video_likes)
    except:
        print(f"Cancion {cancion} no encontrada en YouTube")
        views.append(0)
        likes.append(0)

    try:
        print(f"Escrapeando {cancion} en Shazam")
        link_shazam_search = 'https://www.shazam.com/services/search/v4/es/ES/web/search?term='+cancion['song']+'%20'+cancion['singer']+'&numResults=1&offset=0&types=artists,songs&limit=1'
        json_shazam = json.loads(req.get(link_shazam_search).text)

        song_id = json_shazam['tracks']['hits'][0]['track']['key']
        print(song_id)
        link_shazam_search = 'https://www.shazam.com/services/count/v2/web/track/'+song_id

        json_shazam = json.loads(req.get(link_shazam_search).text)
        shazams_count = json_shazam['total']

        print(shazams_count)    

        #meter aqui la cantidad
        shazams.append(shazams_count)
    except:
        print(f"Cancion {cancion} no encontrada en Shazam")
        shazams.append(0)

    tabla0 = pd.DataFrame()
    tabla0["cancion"] = song
    tabla0["pais"] = pais
    tabla0["views"] = views
    tabla0["likes"] = likes
    tabla0["shazams"] = shazams

    return tabla0


def predicciones(user_songs):

    tabla0 = row_data(user_songs)

    # LIMPIEZA

    # LIMPIEZA SHAZAMS

    int_shazams = []
    for shz in tabla0["shazams"]:
        if shz == "" or shz == 0:
            pass
        elif (type(shz) != int) and ("." in shz):
            int_shazams.append(int(shz.replace(".", "")))
        else:
            int_shazams.append(int(shz))

    shazams_bien = []
    for shz in tabla0["shazams"]:
        if type(shz) != int:
            shazams_bien.append(int(shz.replace(".", "")))
        elif (shz == 0 and type(shz) == int) or (shz == "" and type(shz) != int):
            shazams_bien.append(stats.mean(int_shazams))
        else:
            shazams_bien.append(int(shz))
    tabla0["shazams"] = shazams_bien

    # DAMOS VALOR DE APUESTA DE LA MEDIA HISTÓRICA (20 AÑOS) DEL PAÍS SELECCIONADO
    dictio_odds = {
        0: 342.37403011887017,
        1: 550.0,
        2: 190.04180672268907,
        3: 153.65840943043887,
        4: 303.57951388888887,
        5: 124.09745687748783,
        6: 355.31930026912727,
        7: 265.7936595875654,
        8: 72.9090909090909,
        9: 317.92552826510723,
        10: 304.23496732026143,
        11: 250.0217893876849,
        12: 419.6993137254902,
        13: 164.99074074074073,
        14: 255.3253267973856,
        15: 239.6154970760234,
        16: 116.43540161678706,
        17: 321.21309523809526,
        18: 162.8079961255047,
        19: 114.66420278637773,
        20: 216.79786324786326,
        21: 180.43704850361198,
        22: 270.40350877192986,
        23: 247.20045278637772,
        24: 35.95748225286925,
        25: 334.80882352941177,
        26: 268.8539251896511,
        27: 204.14866099071207,
        28: 234.4282765737874,
        29: 550.0,
        30: 446.10648148148147,
        31: 389.5522875816994,
        32: 68.06107384474257,
        33: 323.12762399077275,
        34: 351.8961076711387,
        35: 153.54299965600276,
        36: 58.391149810801515,
        37: 424.0443756449949,
        38: 300.6666666666667,
        39: 115.6918738468274,
        40: 550.0,
        41: 387.5357920946156,
        42: 130.99342555735745,
        43: 14.644885706914343,
        44: 301.1869806094183,
        45: 142.5697150556129,
        46: 76.81818181818181,
        47: 63.61367202729045,
        48: 67.0881239250086}
    tabla0["bet_mean"] = [dictio_odds[c] for c in tabla0["pais"]]

    # REORDENO TABLA
    tabla0 = tabla0[["pais", "bet_mean", "views", "likes", "shazams"]]
    tabla0.rename(
        columns={
            "pais": "country",
            "views": "views_propos",
            "likes": "likes_propos",
            "shazams": "shazams_propos",
        },
        inplace=True,
    )

    # CREANDO PROPORCIONES
    tabla0["views_propos"] = [
        v / tabla0["views_propos"].sum() for v in tabla0["views_propos"]
    ]
    tabla0["likes_propos"] = [
        l / tabla0["likes_propos"].sum() for l in tabla0["likes_propos"]
    ]
    tabla0["shazams_propos"] = [
        s / tabla0["shazams_propos"].sum() for s in tabla0["shazams_propos"]
    ]
    print(tabla0)

    # PREDICCIONES
    pred = list(ctr.predict(tabla0))
    participantes = len(user_songs)

    prediction_result = []
    for i, dictio in enumerate(user_songs):

        dictio["points"] = round(pred[i] * ((participantes - 1) * 24))
        prediction_result.append(dictio)

    prediction_result = sorted(
        prediction_result, key=itemgetter("points"), reverse=False
    )

    return prediction_result
    
def downloadYouTube(cancion):
    path = 'web/untitled/media'
    url = ("https://www.youtube.com/results?search_query=" + cancion["song"] +
            "+" + cancion["singer"] + "+official")
    link_video = 'https://www.youtube.com/watch?v=' + (req.get(f"{url}")
            .text).split('/watch?v=')[1].split(',')[0].replace('"', "")

    yt = YouTube(link_video)
    yt = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not os.path.exists(path):
        os.makedirs(path)
    yt.download(path, filename='winner.mp4')

def spotify_access_token():
    url = "https://accounts.spotify.com/api/token"

    payload=f"grant_type=refresh_token&refresh_token=AQAdp_4ZFLhLDSe3m6hvmqXfxZFWf2TQkfE35br2EGIFQ80N9t8BWihlDx-f21EgtWIff0TY95mEhNiwq_ryerMSIovlWfrd4q2CiWU-UfpP--UhnqeixNB6Wfj797bfV9M"
    headers = {
      'Authorization': 'Basic ZjA4ZTdkYjM3NTQzNGYzMjllNzMzMjkzMjIzNWFlOWM6YWE0NGE4YjhmODM4NGViYzhhMmNkMGFiYTY1Zjc4YjM=',
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = req.request("POST", url, headers=headers, data=payload).json()

    return response['access_token']
    
def add_to_playlist(tracks):
    tracks = list(reversed(tracks))
    token = spotify_access_token()
    
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : f"Bearer {token}"
        }
    
    
    params_search = {
        "type" : "track",
        "limit":"1"     
        }
    uris_raw = []
    for track in tracks:
        print(f'adding track {track} to spotify playlist')
        params_search['q'] = track['song'] + " " + track['singer']
        
        try:
            response = req.get("https://api.spotify.com/v1/search", headers=headers, params=params_search)
        
            search_content = json.loads(response.text)
            uris_raw.append(search_content['tracks']['items'][0]['uri'])
        except:
            print(f'No es posible añadir canción {track} en lista de spoty')
            pass
        

    uris = ','.join(uris_raw)
    
    
    params_add_track = {
        "position" : "0",
        "uris" : uris # La uri de la canción (canciones)

    }
    playlist_id = "0FNPhJSRpD4mdq0gDEDVWf"

    response = req.post(f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks", headers=headers, params=params_add_track)



connected = set()
countries_choosen = []
user_songs = []
result = []


async def handler(websocket):
    global result
    try:
        print("A client just connected")
        connected.add(websocket)
        send_message = {}
        send_message["type"] = "COUNTRIES_DELETED"
        send_message["value"] = countries_choosen
        await websocket.send(json.dumps(send_message))

        send_message["type"] = "SONGS_PROCESSED"
        send_message["value"] = result
        await websocket.send(json.dumps(send_message))

        try:
            async for message in websocket:
                print("Received message from client: " + message)
                try:
                    dictio = json.loads(message)
                except Exception as e:
                    dictio = []
                if 'type' in dictio:
                    if dictio["type"] == "SONG_CREATED":
                        if 'value' in dictio:
                            song = dictio['value']
                            if set(['song', 'singer', 'country', 'manager']).issubset(set(song.keys())) and song['country']:
                                user_songs.append(song)
                                countries_choosen.append(song["country"])
                                send_message = {}
                                send_message["type"] = "COUNTRIES_DELETED"
                                send_message["value"] = countries_choosen
                                websockets.broadcast(connected, json.dumps(send_message))
                            else:
                                print('Han intentado hackear...')
                        else:
                            print('Han intentado hackear...')


                    elif dictio["type"] == "PROCESS_SONGS":

                        print("Processing songs...")

                        result = predicciones(user_songs)
                        send_message = {}
                        send_message["type"] = "SONGS_PROCESSED"
                        send_message["value"] = result
                        websockets.broadcast(connected, json.dumps(send_message))
                        downloadYouTube(result[len(result)-1])
                        add_to_playlist(result)

                    elif dictio["type"] == "PROCESS_FAKE_SONGS":

                        print("Processing fake songs...")

                        prueba = [{"song":"Dance alone","singer":"Blanks","country":"Germany","manager":"Nony"},
                  {"song":"Dirty Diana","singer":"Michael Jackson","country":"Spain","manager":"Rocío"},
                  {"song":"Warriors","singer":"Imagine Dragons","country":"Sweden","manager":"Miguel Beitia"},
                  {"song":"Shape of You","singer":"Ed Sheeran ","country":"Albania","manager":"Vito"},
                  {"song":"Humble","singer":"Kendrick lamar","country":"Switzerland","manager":"Santi :3"},
                  {"song":"Waka waka","singer":"Shakira","country":"Croatia","manager":"Pepo"},
                  {"song":"Bzr music session ","singer":"Quevedo","country":"Ukraine","manager":"Marta Salvador"},
                  {"song":"Tears","singer":"Clean Bandit","country":"United Kingdom","manager":"Cesar"},
                  {"song":"Nothing else matters","singer":"Metallica","country":"Belgium","manager":"Nelsy"},
                  {"song":"Un golpe de suerte","singer":"Carmen boza","country":"Slovakia","manager":"Mar ;)"},
                  {"song":"La macarena","singer":"Los del rio","country":"Bosnia and Herzegovina","manager":"Inés ba"},
                  {"song":"Despacito ","singer":"Luís Fonsi ","country":"Russia","manager":"Julsssss"},
                  {"song":"Bang bang","singer":"Delaporte","country":"Cyprus","manager":"Unknown"},
                  {"song":"Nothing ese matter","singer":"metallica","country":"Andorra","manager":"Ser"},
                  {"song":"2 Die 4","singer":"Tove Lo","country":"Denmark","manager":"RoberCA"},
                  {"song":"Outrun","singer":"Reckless Love","country":"Finland","manager":"Cesar"},
                  {"song":"Ateo","singer":"C tangana","country":"Czech Republic","manager":"Marta"},
                  {"song":"Zapatillas ","singer":"ECDL","country":"Italy","manager":"DaniM"},
                  {"song":"Under the pressure ","singer":"The war on drugs","country":"Montenegro","manager":"Unknown"},
                  {"song":"Despechá","singer":"Rosalia","country":"Greece","manager":"Abel"},
                  {"song":"Saraluna","singer":"Melendi","country":"Armenia","manager":"Melendi for president"},
                  {"song":"Motomami","singer":"Rosalia","country":"Slovenia","manager":"Javier lázaro"},
                  {"song":"Moscow mule ","singer":"Bad bunny ","country":"Georgia","manager":"David pardo"},
                  {"song":"Elnvolver","singer":"Anitta","country":"Portugal","manager":"Jadde"},
                  {"song":"Motomami","singer":"Rosalia","country":"Hungary","manager":"José Manuel"},
                  {"song":"Canta juegos","singer":"Disney","country":"Lithuania","manager":"Raffa"},
                  {"song":"YOUNGER NOW","singer":"Miley Cyrus","country":"France","manager":"CJ Ramirez"},
                  {"song":"Cheap thrills","singer":"Sia","country":"Australia","manager":"Nhoa"},
                  {"song":"Nothing breaks like a heart","singer":"Miley Cyrus","country":"Estonia","manager":"Maria Miño"},
                  {"song":"Metallica ","singer":"Yung Beef","country":"Austria","manager":"Unknown"},
                  {"song":"Superman","singer":"Bustamante","country":"Azerbaijan","manager":"Unknown"},
                  {"song":"A todos mis amantes","singer":"Rigoberto Bandini","country":"Norway","manager":"Noemí"},
                  {"song":"Mocatriz","singer":"Ojete Calor","country":"Belarus","manager":"Lucia"},
                  {"song":"Paris","singer":"Morat","country":"Bulgaria","manager":"Arturo"},
                  {"song":"Saoko","singer":"Rosalía","country":"Ireland","manager":"Pedro Suárez "},
                  {"song":"Enemy","singer":"Imagine dragons","country":"Iceland","manager":"Marina UX"},
                  {"song":"Quevedo","singer":"C. Tangana","country":"Romania","manager":"Silvia"},
                  {"song":"Clarity","singer":"Zedd feat Roses","country":"Israel","manager":"Manuel"},
                  {"song":"Lalalala","singer":"Andrés Carlos ","country":"Poland","manager":"Unknown"},
                  {"song":"Paradise","singer":"Coldplay","country":"Monaco","manager":"Iñigo"},
                  {"song":"Thriller","singer":"Michael Jackson","country":"San Marino","manager":"Laura"},
                  {"song":"Fiesta pagana ","singer":"Mago de Oz","country":"The Netherlands","manager":"Gonzalo"},
                  {"song":"Imagine","singer":"Beatles ","country":"Moldova","manager":"Alerg"},
                  {"song":"Yonaguni","singer":"Bad Bunny","country":"Latvia","manager":"Sharon"},
                  {"song":"Flying free","singer":"Pont aeri","country":"Serbia and Montenegro","manager":"Alex"},
                  {"song":"Mountain at my gates","singer":"Foals","country":"North Macedonia","manager":"Chris"},
                  {"song":"Hey Mor","singer":"Feid","country":"Turkey","manager":"Juan Cardenas"},
                  {"song":"Here comes the sun ","singer":"The Beatles ","country":"Serbia","manager":"Carolina"},
                  {"song":"Wanabee","singer":"Spice girls ","country":"Malta","manager":"Catalina"}]

                        result = predicciones(prueba)
                        send_message = {}
                        send_message["type"] = "SONGS_PROCESSED"
                        send_message["value"] = result
                        websockets.broadcast(connected, json.dumps(send_message))
                        downloadYouTube(result[len(result)-1])
                        add_to_playlist(result)
                else:
                    print("Han intentado hackear...")

        except websockets.exceptions.ConnectionClosed as e:
            print("A client just disconnected")
        finally:
            print("Entro en finally")
            connected.remove(websocket)

    except Exception as e:

        print("Algo ha fallado")
        raise e


async def main():
    async with websockets.serve(handler, "", 8001):
        print("WELCOME")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
