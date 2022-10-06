# pip install selenium
# pip install webdriver_manager
# pip install catboost
# pip install beautifulsoup4
# pip install requests
# pip install websockets
# pip install -U scikit-learn
# pip3 install openpyxl

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
from joblib import Parallel, delayed
import requests as req
from bs4 import BeautifulSoup as bs
import pandas as pd
import warnings
warnings.filterwarnings("ignore")



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


# IMPORTACIONES
import pandas as pd
from catboost import CatBoostRegressor as CTR
from sklearn.model_selection import train_test_split as tts

print("Importaciones OK")

# CARGAMOS DATA TO TRAIN
data = pd.read_excel("./Excels/Data_to_train.xlsx")
data.drop("Unnamed: 0", axis=1, inplace=True)
print("Carga Data OK")

# PARTIMOS DATA
X = data.drop("propo_puntos", axis=1)
y = data.propo_puntos
X_train, X_test, y_train, y_test = tts(
    X, y, train_size=0.8, test_size=0.2, random_state=22
)
X_train.shape, X_test.shape, y_train.shape, y_test.shape
print("Data partida")

# ENTRENAMOS
print("Entrenando...")
ctr = CTR(iterations=5, verbose=False)
ctr.fit(X_train, y_train)
y_pred = ctr.predict(X_test)
print("Modelo entrenado")

# SACAMOS ERRORES
error = mse(y_test, y_pred, squared=True)
y_pred = ctr.predict(X_test)
R2_test = ctr.score(X_test, y_test)
y_pred = ctr.predict(X_train)
R2_train = ctr.score(X_train, y_train)

if R2_train > (1.15 * R2_test):
    print(
        f"MSE = {error}, R2_train = {R2_train}, R2_test = {R2_test}, OVERFITING (modifica datos)"
    )

elif R2_train > R2_test:
    print(f"MSE = {error}, R2_train = {R2_train}, R2_test = {R2_test}, LO NORMAL")

elif R2_train < R2_test:
    print(
        f"MSE = {error}, R2_train = {R2_train}, R2_test = {R2_test}, UNDERFITING (dame más datos)"
    )


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
        "United Kingdom": 48,
    }
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
        48: 67.0881239250086,
    }
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





import time
import asyncio
import websockets
import json

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
                dictio = json.loads(message)

                if dictio["type"] == "SONG_CREATED":

                    song = dictio["value"]
                    user_songs.append(song)
                    countries_choosen.append(song["country"])
                    send_message = {}
                    send_message["type"] = "COUNTRIES_DELETED"
                    send_message["value"] = countries_choosen
                    websockets.broadcast(connected, json.dumps(send_message))

                elif dictio["type"] == "PROCESS_SONGS":
                   	
                    print("Processing songs...")

                    result = predicciones(user_songs)
                    send_message = {}
                    send_message["type"] = "SONGS_PROCESSED"
                    send_message["value"] = result
                    websockets.broadcast(connected, json.dumps(send_message))

                elif dictio["type"] == "PROCESS_FAKE_SONGS":
                   	
                    print("Processing fake songs...")

                    prueba = [{"song":"Malamente","singer":"Rosalia","country":"Moldova"},
                      {"song":"Volcans","singer":"Buhos","country":"Iceland"},
                      {"song":"Uptown Funk","singer":"Bruno Mars","country":"Austria"},
                      {"song":"As it was","singer":"Harry Styles","country":"Albania"},
                      {"song":"Zumo de Mandrágora","singer":"Piter-G","country":"United Kingdom"},
                      {"song":"Gangstas Paradise","singer":"Coolio","country":"Italy"},
                      {"song":"Provenza","singer":"Karol G","country":"Cyprus"},
                      {"song":"Mon Amour Remix","singer":"Aitana Zzoilo","country":"France"},
                      {"song":"Don't go yet","singer":"Camila Cabello","country":"Greece"},
                      {"song":"Ya no quiero na","singer":"Lola Indigo","country":"Spain"},
                      {"song":"Better man","singer":"Paolo Nutini","country":"Sweden"},
                      {"song":"Camaleón","singer":"Belén Aguilera","country":"Denmark"},
                      {"song":"Crush","singer":"Daft Punk","country":"Lithuania"},
                      {"song":"La mujer de verde","singer":"Izal","country":"Ukraine"},
                      {"song":"Condolence","singer":"Benjamin Clementine","country":"Poland"},
                      {"song":"Pump and the jam","singer":"Technotronic","country":"Malta"},
                      {"song":"Me quedo contigo","singer":"Los chunguitos","country":"Israel"},
                      {"song":"Mi religión","singer":"Nil Moliner","country":"Bulgaria"}]

                    result = predicciones(prueba)
                    send_message = {}
                    send_message["type"] = "SONGS_PROCESSED"
                    send_message["value"] = result
                    websockets.broadcast(connected, json.dumps(send_message))

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
        print("Estoy en async")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
