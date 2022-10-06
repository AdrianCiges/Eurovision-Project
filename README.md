# Eurovision-Project

## ETL
### Obtenemos datos de diferentes fuentes (9) utilizando 4 métodos de extracción.
🎶 Scrappeo Spotify: Duraciones Canciones.

💯 BBDD puntos (ESC DataBase + Wikipedia): Puntos, Idioma, Clasificación, Orden actuación + P% puntos.

🗒️ BBDD Lyrics (Kaggle): Letras, Idioma, Organizador + longitud letra (en palabras), palabras únicas, estructura + NLP (palabras más usadas, temática canción, love song).

🪙 BBDD GDP (Kaggle): GDP anual + posición relativa

📹 Scrappeo Youtube: Views, likes + P% views, likes.

🌍 BBDD Vecinos (Wikipedia): Vecinos + Vecinos participantes por año

💪 BBDD Influencia (TheGoodCountry) -> Score influencia, ranking

❤️ BBDD Reputación (GlobalScan/PIPA) -> Score reputación, ranking

🔎 Scrappeo Shazam: Estilo, shazams

💲 Scrappeo Apuestas: Quostas por año

#### To_SQL: Creamos BBDD + relaciones.
#

## CONTRASTES HIPÓTESIS - ANOVA

### ❌ Variables Descartadas:
Long_letra (p-value: 0.8673152099225407)

Palabras_unicas (p-value: 0.9884527360000015)

TopXword (p-values: 0.21505231118604684, 0.09844530444268441, 0.01598411707225454, 0.19357596722868317, 0.2542394961748323)

Love_Song (p-value: 0.8066218076621867)

Estilos (p-value: 0.45298703184253064)

Duración (p-value: 0.13854202270049623)

Estructura (p-value: 0.5701535767818893)

### ✅ Variables Aceptadas:

País (p-value: 4.1131692326935207e-22)

Idioma (p-value: 3.108737845707387e-61)

Vecinos_participantes (p-value: 3.2383465489737635e-05)

Orden_actuación (p-value: 3.2840140679963695e-05)

Views YT (p-value: 4.382697943679727e-34)

Likes YT (p-value: 1.9082415647254428e-38)

Shazams (p-value: 1.2168547861362296e-35)

GDP (p-value: 6.825147423918337e-06)

Influencia (p-value: 1.1826196448829346e-16)

Reputación (p-value: 3.2714025148511657e-19)
#
## FEATURE IMPORTANCES
### Calculamos pesos de las variables en el cálculo de los puntos (proporción de puntos máximos obtenidos en su edición).

🟢 58% - Likes 

🟢 11% - Odds

🟢 6% - Views

🟢 6% - Shazams

🟢 3% - Country

🔴 2% - Top1word

🔴 2% - Top2word

🔴 2% - Top3word

🔴 1% - Top4word

🔴 1% - Top5word

🔴 1% - Unic_words

🔴 1% - Vecinos_participantes

🔴 1% - Lyric_long

🔴 1% - Idioma

🔴 <1% - Estructura

🔴 <1% - Duración

🔴 <1% - Estilos

🔴 <1% - Love_song 

#### Nos quedamos con las 5 primeras, con las que explicamos el 84% de la varianza.
#

## MACHINE LEARNING

🗑️ Drop 2002/2003: Incoherencia comportamiento de las variables clave (YouTube no existía, comportamiento muy a posteriori)

🤥 Outliers: Definimos lógica propia por la cual son outliera aquellos países con más likes y views que su media en esos 18 años y no obtuvieron una proporción de puntos superior a su media en ese mismo perioro (ojeamos resultados y tiene sentido eliminarlos. Drop 50 registros) 

💻 CatboostRegressor (CTR): iterations = 5 -> R2_train = 0'78, R2_test = 0'76, MSE = 0'007

🤔 Predecimos: Revisamos errores y no son críticos (canciones que sorprendieron en puesta en escena, no predecible).

#
## SCRAPPEO EN CALIENTE
#### Contruimos la arquitectura para el scrappeo en caliente con intención de obtener las variables clave de un número X de canciones de manera instantánea, realizar las covnersiones pertinentes de las mismas, predecir puntuaciones y elaborar un ranking en vivo.

Recibimos canciones: Usamos websockets y una interfaz web propia.

BeautifulSoup: Yotube -> Likes, Views.

Llamada a API: Shazam -> Shazams.

Cruce con BBDD: Bets -> Bet_mean por país.

Transformaciones: Creamos proporciones.

Predicciones.

Creamos ranking: Volcamos resultados en la interfaz web.





