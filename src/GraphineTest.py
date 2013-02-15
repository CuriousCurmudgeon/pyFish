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

from pyFish import Core
from pyFish.Moves import *
from graph.base import Graph
from ContinentBot import ContinentBot

#The id of the game the bot is to play. 
GAME_ID = '73888572'
#The name of the player in the game the bot will be playing for.
PLAYER_NAME = 'The Curmudgeon'
#The cookie the bot will use to authenticate as PLAYER_NAME
COOKIE = 'SESSID=21548ed928da03bb61bade292db94948; LAST=829925F678A3F7AB3A03F11EC9BCBB6800340380D4A4'

bot = ContinentBot(GAME_ID, PLAYER_NAME, COOKIE)

territory = bot.game.map.territories['1']

g = Graph()
g.add_node(territory)

for neighbor in territory.attackable_neighbors.values():
    g.add_node(neighbor)
    g.add_edge(territory, neighbor)

print 
for edge in g.search_edges(start=territory):
    print(edge.end.name.name)