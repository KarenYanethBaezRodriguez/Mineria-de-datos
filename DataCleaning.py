import requests
import io
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
from typing import Tuple, List
import re
from datetime import datetime


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')


def get_csv_from_url(url: str) -> pd.DataFrame:
    s = requests.get(url).content
    return pd.read_csv(io.StringIO(s.decode('utf-8')))


def print_tabulate(df: pd.DataFrame):
    print(tabulate(df, headers=df.columns, tablefmt='orgtbl'))


def limpiar_nombre_dependencia(nombre_sucio: str) -> str:
    nombre_en_partes = nombre_sucio.split(' ')
    return ' '.join(nombre_en_partes[2:])


def obtener_cantidad_de_filas(df: pd.DataFrame) -> int:
    return len(df.index)


def limpiar_dato_sueldo(sueldo_txt: str) -> float:
    return float(sueldo_txt[2:].replace(",", ""))


def get_dependencias_uanl() -> Tuple[List, List[str], List[str]]:
    soup = get_soup(
        f"http://transparencia.uanl.mx/remuneraciones_mensuales/bxd.php")
    table = soup.find_all("table")[0].find_all('tr')
    listado_dependencias = [(option['value'], limpiar_nombre_dependencia(
        option.text)) for option in table[1].find_all("option")]
    listado_meses = [option['value']
                     for option in table[2].find_all('td')[0].find_all("option")]
    listado_anios = [option['value']
                     for option in table[2].find_all('td')[1].find_all("option")]
    return (listado_dependencias, listado_meses, listado_anios)


def get_pages(periodo: str, area: str) -> List[str]:
    soup = get_soup(
        f"http://transparencia.uanl.mx/remuneraciones_mensuales/bxd.php?pag_act=1&id_area_form={area}&mya_det={periodo}")
    try:
        links = soup.find_all("table")[1].find_all('a')
    except Exception as e:
        print(e)
        return []
    return ['1'] + [link.text for link in links]


def get_info_transparencia_uanl(periodo: str, area: str, page: int = 1) -> pd.DataFrame:
    soup = get_soup(
        f"http://transparencia.uanl.mx/remuneraciones_mensuales/bxd.php?pag_act={page}&id_area_form={area}&mya_det={periodo}")
    table = soup.find_all("table")
    try:
        table_row = table[2].find_all('tr')
        list_of_lists = [[row_column.text.strip()
                          for row_column in row.find_all('td')] for row in table_row]
        df = pd.DataFrame(list_of_lists[1:], columns=list_of_lists[0])
        df["Sueldo Neto"] = df["Sueldo Neto"].transform(limpiar_dato_sueldo)
        df = df.drop(['Detalle'], axis=1)
    except Exception as e:
        print(f"pagina sin informacion a: {area}, per: {periodo}, page:{page}")
        print(e)
        df = pd.DataFrame()
    return df


def unir_datos(ldf: List[pd.DataFrame], dependencia: str, mes: str, anio: str) -> pd.DataFrame:
    if len(ldf) > 0:
        df = pd.concat(ldf)
        df["dependencia"] = [dependencia[1]
                             for i in range(0, obtener_cantidad_de_filas(df))]
        df["mes"] = [mes for i in range(0, obtener_cantidad_de_filas(df))]
        df["anio"] = [anio for i in range(0, obtener_cantidad_de_filas(df))]
    else:
        df = pd.DataFrame()
    return df


def wiki() -> pd.DataFrame:
    soup = get_soup("https://en.wikipedia.org/wiki/List_of_states_of_Mexico")
    list_of_lists = []  # :List
    rows = soup.table.find_all('tr')
    for row in rows[1:]:
        columns = row.find_all('td')
        #  listado_de_valores_en_columnas = []
        #  for column in columns:
        #    listado_de_valores_en_columnas.append(coulmn.text.strip())
        listado_de_valores_en_columnas = [
            column.text.strip() for column in columns]
        list_of_lists.append(listado_de_valores_en_columnas)

    return pd.DataFrame(list_of_lists, columns=[header.text.strip() for header in rows[0].find_all('th')])


def remove_repeated_number(str_repeated_value: str) -> float:
    if(type(str_repeated_value) != str):
        str_repeated_value = str(str_repeated_value)
    str_sin_0 = re.sub("^0+", '', str_repeated_value)
    str_sin_comma = str_sin_0.replace(',', '')
    num = 0.0
    if len(str_sin_comma) % 2 == 0:
        mitad = int(len(str_sin_comma)/2)
        num = float(str_sin_comma[0:mitad])
    return num


def remove_repeated_date(str_date_repeated: str) -> datetime:
    return datetime.strptime(str_date_repeated[0:8], '%Y%m%d')


def limpiar_area(area: str) -> Tuple[float, float]:
    str_en_partes = re.findall(r'[\d,\.]*', area)
    str_en_partes.remove('2')
    blancos = str_en_partes.count('')
    for blanco in range(0, blancos):
        str_en_partes.remove('')

    km_str = str_en_partes[0]
    km_float = remove_repeated_number(km_str)
    mi_str = str_en_partes[1]
    mi_float = float(mi_str.replace(',', ''))
    return (km_float, mi_float)


df = pd.read_csv("csv/estados.csv")
df = df.drop(['Coat of arms'], axis=1)
# print(df.columns)
df.columns = ['estado',
              'nombre_oficial',
              'capital', 'ciudad_mas_grande', 'area', 'poblacion_2020',
              'num_de_municipios', 'lugar',
              'fecha_de_admision']
# print(df.columns)
df['lugar'] = df['lugar'].transform(remove_repeated_number)
df['poblacion_2020'] = df['poblacion_2020'].transform(remove_repeated_number)
df['fecha_de_admision'] = df['fecha_de_admision'].transform(
    remove_repeated_date)
areas = df['area'].transform(limpiar_area).to_list()
df['area_km2'] = [a[0] for a in areas]
df['area_mi'] = [a[1] for a in areas]
df = df.drop(['area'], axis=1)
print_tabulate(df)
df.to_csv("csv/estados_limpio.csv", index=False)

# df = wiki()
# print_tabulate(df)
# df.to_csv("csv/estados.csv", index=False)

# listado_dependencias, listado_meses, listado_anios = get_dependencias_uanl()
# ldfs = []
# for anio in listado_anios:
#     for mes in listado_meses:
#         for dependencia in listado_dependencias:
#             pages = get_pages(f"{mes}{anio}", dependencia[0])
#             print(f"m: {mes} a: {anio} d: {dependencia} p: {pages}")
#             ldf = [get_info_transparencia_uanl(f"{mes}{anio}", dependencia[0], page) for page in pages]
#             udf = unir_datos(ldf, dependencia, mes, anio)
#             ldfs.append(udf)
# df = pd.concat(ldfs)
# df.to_csv("csv/uanl.csv", index=False)
