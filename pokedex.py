import requests
import urllib.request
import json
import sqlite3
from bs4 import BeautifulSoup
import plotly.plotly as py
import plotly.graph_objs as go
from PIL import Image
import urllib.request


poke_dict = json.load(open('PokemonFile.json'))



#cacheing for pokemon data from pokeapi
CACHE_FNAME = 'data.json'


try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}


def getWithCaching(pokemon_name):
    baseURL = "http://pokeapi.co/api/v2/pokemon/{}/".format(pokemon_name)
    req = requests.Request(method = 'GET', url =baseURL)
    prepped = req.prepare()
    fullURL = prepped.url

    if fullURL not in CACHE_DICTION:
        response = requests.Session().send(prepped)
        CACHE_DICTION[fullURL] = response.text

    cache_file = open(CACHE_FNAME, 'w')
    cache_file.write(json.dumps(CACHE_DICTION))
    cache_file.close()

    return CACHE_DICTION[fullURL]


#aggregation function of pokemon data from pokeapi
def get_json_from_api(pokemon_name):
    try:
        getWithCaching(pokemon_name)
    except:
        url = "http://pokeapi.co/api/v2/pokemon/{}/".format(pokemon_name)
        response = requests.get(url)
        data = response.json()


    url = "http://pokeapi.co/api/v2/pokemon/{}/".format(pokemon_name)
    response = requests.get(url)
    data = response.json()

    pokemon_list = []

    pokemon_name = data['name']
    pokemon_list.append(pokemon_name)

    type_1 = data['types'][0]['type']['name']
    pokemon_list.append(type_1)

    try:
        type_2 = data['types'][1]['type']['name']
        pokemon_list.append(type_2)
    except:
        type_2 ='N/A'
        pokemon_list.append(type_2)

    speed = data['stats'][0]['base_stat']
    pokemon_list.append(speed)

    defense = data['stats'][3]['base_stat']
    pokemon_list.append(defense)

    attack = data['stats'][4]['base_stat']
    pokemon_list.append(attack)

    special_defense = data['stats'][1]['base_stat']
    pokemon_list.append(special_defense)

    special_attack = data['stats'][2]['base_stat']
    pokemon_list.append(special_attack)

    height = data['height']
    pokemon_list.append(height)

    weight = data['weight']
    pokemon_list.append(weight)

    total_stat = speed + defense + attack + special_defense + special_attack
    pokemon_list.append(total_stat)

    print('_____' * 5)
    print('Name:', pokemon_name.upper())
    try:
        print('Type:', type_1.upper(), 'and' , type_2.upper())
    except:
        print('Type:', type_1.upper())
    print('Speed:', speed)
    print('Defense:', defense)
    print('Attack:', attack)
    print('Special Defense:', special_defense)
    print('Special Attack:', special_attack)
    print('Height:', height, 'inches')
    print('Weight:', weight, 'lbs')
    print('OVERALL STATS:', total_stat)
    print('_____' * 5)
    return pokemon_list


#creates Pokemon and Descriptions tables
def create_table():
    try:
        conn = sqlite3.connect('pokemon.db')
        cur = conn.cursor()
        user_input = input("Remove existing tables? Y/N? ")
        if user_input == "Y":
            statement1 = "DROP TABLE IF EXISTS 'Pokemon';"
            cur.execute(statement1)
        else:
            pass

        table1 = '''
            CREATE TABLE 'Pokemon'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Name' TEXT NOT NULL,
            'Type1' TEXT NOT NULL,
            'Type2' TEXT,
            'TotalStat' INTEGER NOT NULL,
            'Attack' INTEGER NOT NULL,
            'Defense' INTEGER NOT NULL,
            'Speed' INTEGER NOT NULL,
            'SpecialAttack' INTEGER NOT NULL,
            'SpecialDefense' INTEGER NOT NULL,
            'Weight' REAL NOT NULL,
            'Height' INTEGER NOT NULL
            );
            '''
        table2 = '''
            CREATE TABLE 'Descriptions'(
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
            'Descriptions' TEXT
            );
            '''

        cur.execute(table1)
        conn.commit()
        cur.execute(table2)
        conn.commit()
    except:
        print("Error: Connection Issue")


#scrapes pokemon description from veekun
def get_description(pokemon_name):
    veekun_url = 'https://veekun.com/dex/pokemon/{}'.format(pokemon_name)
    page_text = requests.get(veekun_url).text
    soup = BeautifulSoup(page_text, 'html.parser')

    description = soup.find_all('p')


    for p in description:
        if type(description[8]) == str:
            a = description[8]
        else:
            a = description[9]
    print(a.string)



#populates both pokemon and description tables.
#BEWARE takes quite a bit of time to complete!
def populate_pokemon():
    conn = sqlite3.connect('pokemon.db')
    cur = conn.cursor()

    results = json.load(open('data.json'))
    for x in range(1,152):
        data = get_json_from_api(x)

        name = data[0]
        height = data[8]
        weight = data[9]
        type_1 = data[1]
        if type(data[2]) == str:
            type_2 = data[2]
        else:
            type_2= 'N/A'
        speed= data[3]
        attack = data[4]
        defense= data[5]
        special_defense= data[6]
        special_attack= data[7]
        total_stat = data[-1]

        insertion = (None, name, type_1, type_2, total_stat, attack, defense, speed, special_attack, special_defense, weight, height)
        pokemon_insert= '''INSERT INTO Pokemon(Id, Name, Type1,
        Type2, TotalStat, Attack, Defense, Speed, SpecialAttack, SpecialDefense, Weight, Height)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?) '''
        cur.execute(pokemon_insert, insertion)
        conn.commit()

    for x in poke_dict:
        name= (x['Name'])
        try:
            description = get_description(name)
        except:
            description = 'N/A'
        insertion = (None, description)
        pokemon_insert= '''INSERT INTO Descriptions(Id, Descriptions)
        VALUES(?,?) '''
        cur.execute(pokemon_insert, insertion)
        conn.commit()

    print('Done!')


def get_pokemon_sprite(pokemon_name):
    try:
        im = Image.open("{}.png".format(pokemon_name))
        im.show()
    except:
        print("Unable to load image")


#creates a single scatter plot for one pokemon
def create_individual_plotly(pokemon_name_1):
    pokemon_1 = get_json_from_api(pokemon_name_1)
    pokemon1_name = pokemon_1[0]
    pokemon1_speed = pokemon_1[3]
    pokemon1_defense = pokemon_1[4]
    pokemon1_attack = pokemon_1[5]
    pokemon1_specialdefense = pokemon_1[6]
    pokemon1_specialattack = pokemon_1[7]

    pokemon1 = go.Scatter(
    x=[5,10,15,20,25],
    y= [pokemon1_speed, pokemon1_defense, pokemon1_attack, pokemon1_specialattack, pokemon1_specialdefense],
    name= pokemon1_name.upper(),
    text=['Speed', 'Defense', 'Attack','Special Attack', 'Special Defense']
    )

    data = [pokemon1]
    layout=go.Layout(dict(title='STATS OF ' + pokemon1_name.upper()))
    fig = go.Figure(data=data, layout=layout)

    return py.plot(fig, filename='single_pokemon')

#creates a comparison of a scatterplot for two pokemon
def create_comparison_plotly(pokemon_name_1, pokemon_name_2):
    pokemon_1 = get_json_from_api(pokemon_name_1)
    pokemon_2 = get_json_from_api(pokemon_name_2)
    pokemon1_name = pokemon_1[0]
    pokemon1_speed = pokemon_1[3]
    pokemon1_defense = pokemon_1[4]
    pokemon1_attack = pokemon_1[5]
    pokemon1_specialdefense = pokemon_1[6]
    pokemon1_specialattack = pokemon_1[7]

    pokemon2_name = pokemon_2[0]
    pokemon2_speed = pokemon_2[3]
    pokemon2_defense = pokemon_2[4]
    pokemon2_attack = pokemon_2[5]
    pokemon2_specialdefense = pokemon_2[6]
    pokemon2_specialattack = pokemon_2[7]

    pokemon1 = go.Scatter(
    x=[5,10,15,20,25],
    y= [pokemon1_speed, pokemon1_defense, pokemon1_attack, pokemon1_specialattack, pokemon1_specialdefense],
    name= pokemon1_name.upper(),
    text=['Speed', 'Defense', 'Attack','Special Attack', 'Special Defense']
    )
    pokemon2 = go.Scatter(
    x=[5,10,15,20,25],
    y=[pokemon2_speed, pokemon2_defense, pokemon2_attack, pokemon2_specialattack, pokemon2_specialdefense],
    name= pokemon2_name.upper(),
    text=['Speed', 'Defense', 'Attack','Special Attack', 'Special Defense']
    )

    data = [pokemon1, pokemon2]
    layout=go.Layout(dict(title='STAT COMPARISON OF ' + pokemon1_name.upper() + ' & ' + pokemon2_name.upper()))
    fig = go.Figure(data=data, layout=layout)

    return py.plot(fig, filename='compare_pokemon')


#gets top ten pokemon from whole database
def topTen():
    conn = sqlite3.connect('pokemon.db')
    cur = conn.cursor()

    statement = '''SELECT Name, Type1, TotalStat, Attack, Defense,
                Speed, SpecialAttack, SpecialDefense FROM Pokemon '''
    statement += 'GROUP BY TotalStat Order By TotalStat DESC LIMIT 10'

    cur.execute(statement)
    a = cur.fetchall()
    count = 1
    for row in a:
        print(count)
        print(row[0].upper(),'Type:', row[1].upper(), 'Total Stats:', row[2])
        print('Attack:', row[3], 'Defense:', row[4], 'Speed:', row[5], 'Special Attack:', row[6], 'Special Defense:', row[7])
        print('__________' * 3)
        count = count +1

#gets top ten pokemon by type
def topByType(type):
    conn = sqlite3.connect('pokemon.db')
    cur = conn.cursor()

    statement = '''SELECT Name, Type1, TotalStat, Attack, Defense,
                Speed, SpecialAttack, SpecialDefense FROM Pokemon '''
    statement += 'WHERE Type1 = "{}"'.format(type)
    statement += 'GROUP BY TotalStat Order By TotalStat DESC LIMIT 10'

    cur.execute(statement)
    a = cur.fetchall()
    count = 1
    for row in a:
        print(count)
        print(row[0].upper(),'Type:', row[1].upper(), 'Total Stats:', row[2])
        print('Attack:', row[3], 'Defense:', row[4], 'Speed:', row[5], 'Special Attack:', row[6], 'Special Defense:', row[7])
        print('__________' * 3)
        count = count +1


#code for interaction
def interactive_prompt():
    print("-----------------------------------------------")
    print("Hello young trainer! What would you like to do?")
    print("Enter:")
    print("'pokemon'  + 'pokemon name' to see stats")
    print("'picture'  + 'pokemon name' to see a picture")
    print("'info'     + 'pokemon name' to see a description")
    print("'compare1' + 'pokemon name' to see their stats in a graph")
    print("'compare2' + 'two pokemon names' to compare their stats")
    print("'type'     + 'name of type' to see top pokemon of this type")
    print("'top pokemon' +  to see the top pokemon of this generation")
    print("Need a reminder? Type 'all pokemon' to see a complete list!")
    print("-----------------------------------------------")


    response = ''
    while response != 'exit':
        response = input('Enter a command: ')

        if response == 'all pokemon':
            for x in poke_dict:
                print(x['Name'])

        if response == 'exit':
            print("Safe travels Trainer!")
            break

        if response.split()[0] == 'picture':
            pokemon_name = response.split()[1]
            get_pokemon_sprite(pokemon_name)

        if response.split()[0] == 'info':
            pokemon_name = response.split()[1]
            print(pokemon_name.upper(),'INFO:')
            get_description(pokemon_name)

        if response.split()[0] == 'pokemon':
            pokemon_name = response.split()[1]
            get_json_from_api(pokemon_name)

        if response.split()[0] == 'compare1':
            pokemon_name = response.split()[1]
            create_individual_plotly(pokemon_name)

        if response.split()[0] == 'compare2':
            pokemon_name_1 = response.split()[1]
            pokemon_name_2 = response.split()[2]
            create_comparison_plotly(pokemon_name_1, pokemon_name_2)

        if response == 'top pokemon':
            topTen()

        if response.split()[0] == 'type':
            response = response.split()
            type = response[1]
            topByType(type)

        if 'compare2' or 'compare1' or 'info' or 'picture' or 'type' or 'exit' or 'top pokmeon' or 'all pokemon' not in response.split()[0]:
            print("Unrecognized command, try again!")

        else:
            response = print('Enter another command!')



if __name__=="__main__":
    interactive_prompt()
