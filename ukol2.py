import json, os
from pyproj import CRS, Transformer
from math import sqrt
import argparse

path_kontejnery = "kontejnery.geojson"
path_adresy = "adresy.geojson"

'''Soubory jako parametry programu. -h zobrazi napovedu.'''
parser = argparse.ArgumentParser(description = "Vypocet vzdalenosti ke kontejnerum na trideny odpad")
parser.add_argument('-a', '--adresni_body', type = str, metavar = '', required = False, help = 'GeoJSON s adresnimi body.')
parser.add_argument('-k', '--kontejnery', type = str, metavar = '', required = False, help = 'GeoJSON s kontejnery.')
args = parser.parse_args()
if args.adresni_body is not None:
    path_adresy = args.adresni_body
if args.kontejnery is not None:
    path_kontejnery = args.kontejnery

def load_file(path):
    '''Nacteni vstupniho souboru. Pokud soubor chybi (spatne zadana cesta), vyskoci chyba.'''
    try:
        with open(path, encoding="UTF-8") as json_file:
            return json.load(json_file)["features"]
    except ValueError: 
        print(f"Soubor {path} neni validni GeoJSON.")
        exit()
    except FileNotFoundError:
        print(f"Vstupni data {path} se nepodarilo nalezt, zkontrolujte cestu.")
        exit()
    except PermissionError:
        print(f"Vstupni data {path} existuji, ale program k nim nema pristup.")
        exit()

wgs2jtsk = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(5514))

def pythagor(x, y):
    '''Pythagorova veta.'''
    return sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)

def distance (adresy, kontejnery):
    '''Vypocet vzdalenosti mezi adresnimi body a kontejnery. Vysledek uklada do slovniku.'''
    distances = {}
    for (adresy_street, adresy_coor) in adresy.items():
        dismin = 10000
        for (kontejnery_street, kontejnery_coor) in kontejnery.items():
            dis = pythagor(adresy_coor, kontejnery_coor)
            if dis > 10000:
                print(f"Nejblizsi kontejner pro adresu {(adresy_street)} je dale, nez 10 km. Program skonci.")
                exit()
            if dis < dismin:
                dismin = dis
        distances[adresy_street] = dismin
    return distances

def median(distances):
    '''Vypocet medianu ze vzdalenosti.'''
    v_list = []
    for (street, dis) in distances.items(): #vytvoreni listu vzdalenosti
        v_list.append(dis)
    v_list.sort() #serazeni listu podle vzdalenosti
    mid = ((len(v_list)-1)/2) #zjisteni prostredniho prvku
    if (len(v_list) % 2) == 0:  #pokud je median sude cislo 
        mid1 = int(mid - 0.5)
        mid2 = int(mid + 0.5)
        med = (v_list[mid1]+v_list[mid2])/2
    else:  #pokud je median liche cislo
        mid = int(mid + 0.5)
        med = v_list[mid]
    return med

def adresy_dict(json_adresy):
    '''Vytvoreni slovniku adres s pozadovanymi atributy.'''
    adresy = {}
    for feature in json_adresy:
        street = feature["properties"]["addr:street"] + " " + feature["properties"]["addr:housenumber"]
        wgs_lat = feature["geometry"]["coordinates"][1]
        wgs_lon = feature["geometry"]["coordinates"][0]
        adresy[street] = wgs2jtsk.transform(wgs_lat, wgs_lon) #volani promenne na prevod wgs do s-jtsk
    return adresy

def kontejnery_dict(json_kontejnery):
    '''Vytvoreni slovniku kontejneru s pozadovanymi atributy.'''
    kontejnery = {}
    for feature in json_kontejnery:
        street = feature["properties"]["STATIONNAME"]
        latlon = feature["geometry"]["coordinates"]
        access = feature["properties"]["PRISTUP"]
        # uvazujeme pouze volne pristupne kontejnery
        if access=="volně":
            kontejnery[street] = latlon
    return kontejnery

json_adresy = load_file(path_adresy)
json_kontejnery = load_file(path_kontejnery)

adresy = adresy_dict(json_adresy)
kontejnery = kontejnery_dict(json_kontejnery)

print(f"Nacteno {len(adresy)} adresnich bodu.")
print(f"Nacteno {len(kontejnery)} kontejneru na trideny odpad.")
print()

distances = distance(adresy, kontejnery) #vypocet vzdalenosti ke kontejnerum

average = (sum(distances.values()) / len(distances)) #vypocet prumerne vzdalenosti ke kontejneru
print(f"Prumerna vzdalenost ke kontejneru je {average:.0f} m.")

maximum = max(distances.values()) #vypocet maximalni vzdalenosti ke kontejneru
for (street, dis) in distances.items():
    if dis == maximum:
        maxstreet = street
print(f"Nejdale ke kontejneru je z adresy {maxstreet} a to {maximum:.0f} m.")
print()

med = median(distances)
print(f"Median vzdalenosti ke kontejneru je {med:.0f} m.")

