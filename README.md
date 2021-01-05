# 2. domácí úkol - Úvod do programování

Skript, vytvořený v rámci předmětu Úvod do programování na PřF UK, zimní semestr 2020/2021. 
Kód má zhodnotit dostupnost kontejnerů tříděného odpadu v jednotlivých čtvrtích. Ze vstupních dat tedy zjišťuje průměrnou a maximální vzdálenost ke kontejnerům. 
Link na zadání: https://github.com/xtompok/uvod-do-prg_20/tree/master/du02

<h3> Vstup </h3>

Vstupními daty jsou dva soubory GeoJSON, jeden představuje adresní body a druhý rozmístění kontejnerů. V obou případech se tedy jedná 
o bodová data. 

U adresních bodů je očekáván souřadnicový systém WGS-84 (EPSG: 4326) a požadován je atribut `addr:street` a `addr:housenumber` s klíčem `properties` a `coordinates` s klíčem `geometry`. 

Kontejnery mají mít souřadnicový systém S-JTSK (EPSG: 5514) a klíč `properties` má obsahovat `STATIONNAME` a `PRISTUP`. Klíč `geometry` opět `coordinates`.

Cesty ke vstupním souborům jsou zapsány přímo ve skriptu (předpokládá se umístění ve stejné složce, jako je skript). Dále byl využit modul [`argparse`](https://docs.python.org/3/library/argparse.html), kde se volitelně dají upravit vstupní
soubory zadáním argumentu -a pro adresy či -k pro kontejnery. Ve chvíli, kdy argumenty zadány nejsou, skript počítá s cestami, vepsanými do skriptu.  

<h3> Nahrání dat, validace </h3>

V úvodu jsou nahrána vstupní data pomocí funkce `load_file`. Tato funkce ověřuje, zdali je soubor nalezen. Pokud ne, skript skončí chybou.
Druhá funkce `load_json` ověří, zdali se jedná o validní JSON. V případě, že struktura není čitelná, program skončí chybou. 

Následuje funkce `wgs2jtsk`, která pomocí modulu [`pyproj`](https://pypi.org/project/pyproj/) převádí vstupní data, která jsou v souřadnicovém systému WGS84 
do souřadnicového systému S-JTSK. Děje se tak pro ulehčení následujících výpočtů, kde v S-JTSK se dá spočítat vzdálenost Pythagorovou větou. 

Po nahrání dat a vytvoření JSONu následuje vytvoření slovníku adres a kontejnerů čtením požadovaných atributů ve slovnících `json_adresy` a `json_kontejnery`. Délka obou slovníků je vypsána jako počet vstupních adres a kontejnerů. 

<h3> Výpočet vzdáleností </h3>

Pro výpočet vzdáleností slouží funkce `distances`, jejímž vstupem je právě slovník adres a kontejnerů. Pro každou adresu jsou procházeny všechny kontejnery a počítána
vzdálenost ke každému kontejneru, načež minimální vzdálenost (tedy k nejbližšímu kontejneru) se uloží do nového slovníku, kde klíčem je adresa a atributem vzdálenost. 
Pokud vzdálenost k libovolnému kontejneru překročí 10 km, program skončí chybou. 

Z tohoto slovníku je počítána průměrná vdálenost, kde suma všech vzdáleností je dělena počtem adresních bodů. 
Skript zjišťuje maximální vzdálenost ke kontejneru od adresního bodu a následně ji vypisuje spolu s příslušnou adresou. 

Další představuje `median`, kde je proveden výpočet mediánu vdzáleností. Výpočet je proveden skrze seznam, který je setřízen a probíhá zjištění, zdali
je středový bod sudý či lichý. V případě lichého medián představuje středový prvek, v případě sudého aritmetický průměr dvou středových vzdáleností. 

<h3> Výstup </h3>

Výstup z programu s přiloženými daty je následující: 

```
Nacteno 26 adresnich bodu.
Nacteno 4 kontejneru na trideny odpad.

Prumerna vzdalenost ke kontejneru je 52 m.
Nejdale ke kontejneru je z adresy Na Františku 847/8 a to 185 m.

Median vzdalenosti ke kontejneru je 44 m.
```
