import csv
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

defaultUrl = "https://wiki.pokemoncentral.it/"


def getGeneration(id):
    if id <= 151:
        return 1
    elif id <= 251:
        return 2
    elif id <= 386:
        return 3
    elif id <= 493:
        return 4
    elif id <= 649:
        return 5
    elif id <= 721:
        return 6
    elif id <= 809:
        return 7
    elif id <= 905:
        return 8
    else:
        return 9


def genToString(gen):
    if gen == 1:
        return 'prima'
    elif gen == 2:
        return 'seconda'
    elif gen == 3:
        return 'terza'
    elif gen == 4:
        return 'quarta'
    elif gen == 5:
        return 'quinta'
    elif gen == 6:
        return 'sesta'
    elif gen == 7:
        return 'settima'
    elif gen == 8:
        return 'ottava'


def getOldDataList(table):
    data_list = []

    # Itera attraverso le righe della tabella escludendo l'intestazione
    for row in table.select('tr')[2:]:
        # Estrai i dati dalle colonne

        columns = row.select('td')

        if len(columns) < 6:
            break

        lv = columns[0].text.strip().replace('Inizio', '1')
        mossa = columns[1].text.strip()
        tipo = columns[2].text.strip()
        potenza = columns[3].text.strip().replace('—', '-')
        precisione = columns[4].text.strip().replace('—', '-')
        pp = columns[5].text.strip()

        data_list.append({
            'Lv.': lv,
            'Mossa': mossa,
            'Tipo': tipo,
            'Potenza': potenza,
            'Precisione': precisione,
            'PP': pp
        })

    return data_list


def getDataList(table, gen):
    data_list = []

    if gen < 4:
        return getOldDataList(table)

    # Itera attraverso le righe della tabella escludendo l'intestazione
    for row in table.select('tr')[2:]:
        # Estrai i dati dalle colonne

        columns = row.select('td')

        if len(columns) < 7:
            break

        lv = columns[0].text.strip().replace('Inizio', '1')
        mossa = columns[1].text.strip()
        tipo = columns[2].text.strip()
        categoria = columns[3].text.strip()
        potenza = columns[4].text.strip().replace('—', '-')
        precisione = columns[5].text.strip().replace('—', '-')
        pp = columns[6].text.strip()

        data_list.append({
            'Lv.': lv,
            'Mossa': mossa,
            'Tipo': tipo,
            'Categoria': categoria,
            'Potenza': potenza,
            'Precisione': precisione,
            'PP': pp
        })

    return data_list


def scraping(pokemon, id, path):
    if int(id) > 1010:
        return

    if int(id) != 29 and int(id) != 32:
        return

    url = defaultUrl + pokemon
    path = os.path.join(defaultPath, id)
    csvFile = os.path.join(path, "gen9.csv")
    response = requests.get(url)
    gen = getGeneration(int(id))
    mainPageError = False

    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        if os.path.exists(csvFile):
            return

    if int(id) == 29:
        url = "https://wiki.pokemoncentral.it/Nidoran" + quote('♀')
    elif int(id) == 32:
        url = "https://wiki.pokemoncentral.it/Nidoran" + quote('♂')

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")


        table = soup.find('table', class_='white-rows max-width-xl-100 width-xl-100 no-border-spacing')
        if table is None:
            table = soup.find('table', class_='roundy text-center pull-center white-text')
        if table is None:
            table = soup.find('table', class_='roundy pull-center text-center')

        if table is not None:
            # Inizializza una lista vuota per memorizzare i dati
            data_list = getDataList(table, 9)

            # Intestazioni delle colonne
            headers = ['Lv.', 'Mossa', 'Tipo', 'Categoria', 'Potenza', 'Precisione', 'PP']

            # Scrivi i dati nel file CSV
            with open(csvFile, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data_list)

            print(f"I dati di numero {id}, {pokemon}, sono stati salvati in {csvFile}")

        else:
            mainPageError = True

    else:
        print('Error')

    while gen < 9:
        oldGenUrl = url + '/Mosse_apprese_in_' + genToString(gen) + '_generazione'
        csvOldFile = os.path.join(path, "gen" + str(gen) + ".csv")
        response = requests.get(oldGenUrl)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            table = soup.find('table', class_='white-rows max-width-xl-100 width-xl-100 no-border-spacing')
            if table is None:
                table = soup.find('table', class_='roundy pull-center text-center')

            data_list = getDataList(table, gen)

            # Intestazioni delle colonne
            if gen <= 3:
                headers = ['Lv.', 'Mossa', 'Tipo', 'Potenza', 'Precisione', 'PP']
            else:
                headers = ['Lv.', 'Mossa', 'Tipo', 'Categoria', 'Potenza', 'Precisione', 'PP']

            # Scrivi i dati nel file CSV
            with open(csvOldFile, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data_list)

            if gen == 8 and mainPageError:
                csvOldFile = os.path.join(path, "gen9.csv")
                with open(csvOldFile, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(data_list)

            print(f"I dati di {pokemon} sono stati salvati in {csvOldFile}")

        else:
            print(f"Errore prendendo i dati di {pokemon} per la generazione {gen}!")

        gen += 1


if __name__ == '__main__':

    with open('res/pokemon.csv') as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        defaultPath = os.path.join(os.getcwd(), 'moves')
        if not os.path.isdir(defaultPath):
            os.mkdir(defaultPath)

        for row in csv_reader:

            if line_count >= 29 and line_count <= 34:
                scraping(row[1], row[0], defaultPath)

            else:
                line_count += 1
