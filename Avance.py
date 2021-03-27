import numpy as np  # algebra lineal
import pandas as pd
import matplotlib.pyplot as plt

datos = pd.read_csv('D:\FCFM\Mineria-de-datos\csv\MXvideos.csv')

datos = datos.drop(['video_id', 'trending_date', 'category_id', 'tags', 'thumbnail_link',
                   'comments_disabled', 'ratings_disabled', 'video_error_or_removed'], axis=1)

datos.to_csv("csv/MXvideos_Limpio.csv", index=False)

datos.likes.plot(kind = "line", color = "blue",label = "likes",linewidth=0.5,alpha = 1,grid = False,linestyle = "--")
datos.dislikes.plot(color = "red",label = "dislikes",linewidth=0.5, alpha = 1,grid = False,linestyle = ":")
plt.legend(loc='upper left')
plt.ylabel("Dislikes")
plt.xlabel("Likes")
plt.title("Likes/Dislikes Tabla")
plt.show()
