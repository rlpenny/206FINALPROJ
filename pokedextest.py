import unittest
import pokedex as pokedex
import json
import requests
import sqlite3



class TestDatabase(unittest.TestCase):

    def testDatabase(self):
        conn = sqlite3.connect('pokemon.db')
        cur = conn.cursor()

        #testing whether database has all 151 pokemon
        sql = '''SELECT Name FROM Pokemon'''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 151)
        self.assertIn(('ditto',), result_list)
        self.assertIn(('pidgey',), result_list)
        self.assertIn(('pikachu',), result_list)
        self.assertIn(('dewgong',), result_list)

        #checking to see if description database is correct
        sql = 'SELECT Descriptions FROM Descriptions'
        results = cur.execute(sql)
        result_list = results.fetchall()

        self.assertEqual(len(result_list), 151)
        self.assertIn('A strange seed was planted on its back at birth. The plant sprouts and grows with this Pokémon.', result_list[0])
        self.assertIn('When tapped, this Pokémon will pull in its head, but its tail will still stick out a little bit.', result_list[7])
        self.assertIn('A very haughty Pokémon. Among fans, the size of the jewel in its forehead is a topic of much talk.', result_list[52])
        self.assertIn('It can fly in spite of its big and bulky physique. It circles the globe in just 16 hours.', result_list[-3])
        conn.close()
#
class TestAPIData(unittest.TestCase):

    def testAPICollection(self):
        #testing api collection
        pokemon_list = pokedex.get_json_from_api('bulbasaur')
        self.assertEqual(len(pokemon_list), 11)
        self.assertEqual(pokemon_list[0], "bulbasaur")
        self.assertEqual(pokemon_list[1], "poison")
        self.assertEqual(pokemon_list[2], "grass")
        self.assertEqual(pokemon_list[3], 45)
        self.assertEqual(pokemon_list[4], 49 )
        self.assertEqual(pokemon_list[5], 49)
        self.assertEqual(pokemon_list[6], 65)
        self.assertEqual(pokemon_list[7], 65)
        self.assertEqual(pokemon_list[8], 7)
        self.assertEqual(pokemon_list[9], 69)
        self.assertEqual(pokemon_list[10], 273)




if __name__ == '__main__':
    unittest.main()
