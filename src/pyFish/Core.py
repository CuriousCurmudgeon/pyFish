#Copyright 2009 Brian Meeker
#
#This file is part of pyFish.
#
#pyFish is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#pyFish is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with pyFish.  If not, see <http://www.gnu.org/licenses/>.

import json
import urllib.request
from graph.base import Graph
from pyFish.Moves import *

WARFISH_URL = 'http://216.169.106.90/war/services/rest'
#WARFISH_URL = 'http://warfish.net/war/services/rest'
WARFISH_METHODS = {'details': 'warfish.tables.getDetails',
                   'state': 'warfish.tables.getState',
                   'history': 'warfish.tables.getHistory',
                   'doMove': 'warfish.tables.doMove'}
NONE, LIGHT, MODERATE, FOGGY, VERY, EXTREME = range(6) 
TURN_BASED, AUTO, BLIND_AT_ONCE = range(3)

def initialize_game(game_id, cookie):
    """Pulls down all of the game information from Warfish and creates a Game object."""
    
    details = request_game_info(WARFISH_METHODS['details'], game_id, cookie, sections=('board', 'rules', 'map', 'continents'))
    state = request_game_info(WARFISH_METHODS['state'], game_id, cookie, sections=('players', 'board', 'possibleactions'))
    #TODO: Right now this assumes their are no more than 1500 moves. This is incorrect and needs fixed at some point.
    history = request_game_info(WARFISH_METHODS['history'], game_id, cookie, additional_parameters={'start': '-1', 'num': '1500'})
    
    players = {player_info['id'] : Player(player_info) for player_info in state['_content']['players']['_content']['player']}
    map = Map(details['_content']['map']['_content']['territory'], 
              details['_content']['board']['_content']['border'],
              details['_content']['continents']['_content']['continent'],
              state['_content']['board']['_content']['area'],
              players)
    rules = Rules(details['_content']['rules'])  
    history = History.process_history(history['_content']['movelog']['_content']['m'])
    possible_actions = []
    if '_content' in state['_content']['possibleactions']:
        for action in state['_content']['possibleactions']['_content']['action']:
            possible_actions.append(action['id'])
    
    return Game(game_id, map, players, rules, history, cookie, possible_actions)

def request_game_info(method, game_id, cookie, sections=None, additional_parameters=None):
    """Make a request to Warfish and return the results as a dictionary."""
    
    url = '{0}?_method={1}&gid={2}&_format=json'.format(WARFISH_URL, method, game_id)
    if sections:
        url += '&sections={0}'.format(','.join(sections))
    if additional_parameters:
        url += ''.join(['&%s=%s' % item for item in additional_parameters.items()])
    request = urllib.request.Request(url, None, {'Cookie': cookie} )
    response = urllib.request.urlopen(request)
    return json.loads(bytes.decode(response.read()))

"""Represents a Warfish game. This is currently limited to only supporting 
a standard game of Risk. While Warfish allows customization of rules this is not currently supported."""
class Game:
    
    def __init__(self, id, map, players, rules, history, cookie, possible_actions):
        """Initializes a game with the given map and players."""
        self.id = id
        self.map = map
        self.players = players
        self.rules = rules
        self.history = history
        self.cookie = cookie
        self.possible_actions = possible_actions
        self.last_move = None
    
    def execute_move(self, move):
        complete_url = '{0}?_method={1}&gid={2}{3}&_format=json'.format(WARFISH_URL, WARFISH_METHODS['doMove'], self.id, move.to_query_string())
        print(complete_url)
        
        request = urllib.request.Request(complete_url, None, {'Cookie': self.cookie} )
        move_response = urllib.request.urlopen(request)
         
        move_result = MoveResults.process_move_result(json.loads(bytes.decode(move_response.read())), move, self)
        self.last_move = move
        return move_result

"""A map in Warfish is made up of territories, which can be organized into continents."""
class Map(Graph):
    
    def __init__(self, map_dictionary, board_dictionary, continents_dictionary, board_state_dictionary, players_dictionary):
        super().__init__()
        self.territories = [self.add_node(Territory(item)) for item in map_dictionary]
        self.continents = {item['id'] : Continent(item, self.territories) for item in continents_dictionary}
        #Each board element has two ids. a is the attacking country and b is the defending country.
        for item in board_dictionary:
            territory_a = self.territories[item['a']]
            territory_b = self.territories[item['b']]
            territory_a.attackable_neighbors[territory_b.id] = territory_b
            territory_b.defendable_neighbors[territory_a.id] = territory_a
        #Assign each territory an owner.
        for item in board_state_dictionary:
            #A playerid of -1 means the territory is neutral
            territory = self.territories[item['id']]
            if item['playerid'] != '-1':
                player = players_dictionary[item['playerid']]
                territory.owner = player
                player.territories.append(territory)
            if item['units'] != '?':
                territory.armies = int(item['units'])

"""A continent represents a collection of territories that give a bonus when controlled by a single player."""
class Continent:
    
    def __init__(self, continent_dictionary, territories):
        self.name = continent_dictionary['name']
        self.id = continent_dictionary['id']
        self.bonus = int(continent_dictionary['units'])
        self.territories = {}
        for id in continent_dictionary['cids'].split(','):
            for key, value in territories.items():
                if key == id:
                    self.territories[key] = value
                    
"""Represents a player in a game of Warfish."""
class Player:
        
    def __init__(self, player_dictionary):
        self.name = player_dictionary['name']
        self.is_turn = player_dictionary['isturn'] != 0
        self.active = player_dictionary['active'] != 0
        self.team_id = int(player_dictionary['teamid'])
        if player_dictionary['units'] != '?':
            self.reserve_units = int(player_dictionary['units'])  
        self.profile_id = player_dictionary['profileid']
        self.id = int(player_dictionary['id'])
        self.cards = ()
        self.territories = []

"""Warfish rules are highly customizable. The Rules class represents the rules
for a particular game."""
class Rules:

    def __init__(self, rules_dictionary):
        """The following values in the dictionary are currently unknown and unmapped:
            * keeppossession - I think this deals with keeping possession when abandoning territories but I am not sure.
            * keeppossessiononexpire - I don't know how this differs from keeppossession
            * numpercountry - I don't know how this differs from maxpercountry"""
        self.num_attacks = rules_dictionary['numattacks']
        self.num_transfers = rules_dictionary['numtransfers']
        self.pre_transfers = rules_dictionary['pretransfer']
        self.damage_dice_attack = rules_dictionary['afdie']
        self.damage_dice_defend = rules_dictionary['dfdie']
        self.allow_abandon = rules_dictionary['allowabandon'] != 0
        self.card_scale = rules_dictionary['cardscale'].split(",")
        self.next_cards_worth = rules_dictionary['nextcardsworth'].split(",")
        self.num_reserves = rules_dictionary['numreserves']
        self.allow_return_to_attack = rules_dictionary['returntoattack'] != 0
        self.allow_return_to_placement = rules_dictionary['returntoplace'] != 0
        self.max_armies_per_country = rules_dictionary['maxpercountry']
        self.fog = rules_dictionary['fog']
        self.attack_die_sides = rules_dictionary['adie']
        self.defend_die_sides = rules_dictionary['ddie']
        self.is_blind_at_once_play = rules_dictionary['baoplay'] != 0
        self.is_team_game = rules_dictionary['teamgame'] != 0
        self.allow_team_transfer = rules_dictionary['teamtransfer'] != 0
        self.allow_continuous_attack = rules_dictionary['continuousattack'] != 0
        self.boot_time = rules_dictionary['boottime']
        self.is_card_capture = rules_dictionary['hascards'] != 0 #TODO: I am not positive that this is actually a setting for card capture. I need to play with it.
        self.allow_team_place_units = rules_dictionary['teamplaceunits'] != 0
        self.initial_unit_placement = rules_dictionary['uplace'] #I think this has to do with the initial unit placement mechanism used.
        self.card_sets_traded = rules_dictionary['cardsetstraded']

"""A map is made up of many territories, each of which must have an owner and armies."""
class Territory:

    def __init__(self, territory_dictionary):
        self.name = territory_dictionary['name']
        self.max_units = territory_dictionary['maxunits'] 
        self.id = territory_dictionary['id']
        self.owner = None
        self.attackable_neighbors = {}
        self.defendable_neighbors = {}
        self.armies = 0

"""A turn is made up of a collection of moves."""
class Turn:

    def __init__(self, moves, index=0):
        self.moves = moves
        self.index = index
    
if __name__ == "__main__":
    import doctest
    doctest.testmod()