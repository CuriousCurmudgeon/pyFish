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


#You must provide values for the following variables

#The id of the game the bot is to play. 
GAME_ID = ''
#The name of the player in the game the bot will be playing for.
PLAYER_NAME = ''
#The cookie the bot will use to authenticate as PLAYER_NAME
COOKIE = '' 

"""A basic bot with no intelligence that can successfully complete moves.
It has no error handling."""
class RandomBot:
    
    def __init__(self, game_id, player_name, cookie):
        self.game = Core.initialize_game(game_id, cookie)
        self.player = None
        for player_id, player in self.game.players.items():
            if(player.name == player_name):
                self.player = player
                break
        
    def take_turn(self):
        """Execute a full turn."""
        while len(self.game.possible_actions) > 0:
            move_result = None
            if 'placeunits' in self.game.possible_actions:
                print('\r\nPlacing Units')
                move_result = self.place_units()
            elif 'attack' in self.game.possible_actions:
                print('\r\nAttacking')
                attack_targets = self.find_attack_targets()
                if len(attack_targets) > 0:
                    move_result = self.attack(attack_targets)
                else:
                    self.game.possible_actions.remove('attack')
            elif 'transfer' in self.game.possible_actions:
                print('\r\nSkipping Transfers')
                self.game.possible_actions.remove('transfer')
            elif 'endturn' in self.game.possible_actions:
                print('\r\nEnding Turn')
                self.game.execute_move(Moves.EndTurnMove())
                break
            else:
                print("\r\nNo valid move found")
            if move_result != None:
                self.game.possible_actions = move_result.possible_actions
                print(move_result)
        print("\r\nTurn Complete")
    
    def place_units(self):
        """Places units round robin on the board until they have all been placed."""
        remaining_units = self.player.reserve_units
        territory_dict = {}
        while remaining_units > 0:
            for territory in self.player.territories:
                territory_dict[territory] = 1
                remaining_units -= 1
                if remaining_units == 0:
                    break
        place_units_move = Moves.PlaceUnitsMove(territory_dict)
        return self.game.execute_move(place_units_move)
    
    def find_attack_targets(self):
        """Finds all territories that the bot controls with 4 or more armies and the neighbors that 
        can be attacked from that territory."""
        can_attack_from = {}
        for territory in self.player.territories:
            if territory.armies >= 4:
                for attackable_neighbor in territory.attackable_neighbors.values():
                    if attackable_neighbor.owner != self.player:
                        if territory not in can_attack_from:
                            can_attack_from[territory] = []
                        can_attack_from[territory].append(attackable_neighbor)
        return can_attack_from
    
    def attack(self, attack_targets):
        """Picks one of the attack_targets and attacks it continuously. It will also handle
        the free transfer after capturing a territory if needed."""
        for territory, attackable_neighbors in attack_targets.items():
            for neighbor in attackable_neighbors:
                attack_move = Moves.AttackMove(territory, neighbor, territory.armies-1, True)
                attack_move_result = self.game.execute_move(attack_move)
                if attack_move_result.captured and 'freetransfer' in attack_move_result.possible_actions:
                    #Move all but one of the remaining armies to the captured territory.
                    free_transfer_move = Moves.FreeTransferMove(territory.armies - 1)
                    free_transfer_move_result = self.game.execute_move(free_transfer_move) 
                return attack_move_result
            
bot = RandomBot(GAME_ID, PLAYER_NAME, COOKIE)
bot.take_turn()