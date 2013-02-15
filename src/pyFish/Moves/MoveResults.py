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

"""This module provides classes for the results of moves."""

import abc

class MoveResult(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def __init__(self, move_result_dictionary):
        print(move_result_dictionary)
        self.result_code = move_result_dictionary['_content']['return']['code']
        self.result_message = move_result_dictionary['_content']['return']['msg']
        self.possible_actions = []
        for action in move_result_dictionary['_content']['return']['_content']['possibleactions']['_content']['action']:
            self.possible_actions.append(action['id'])
       
    @abc.abstractmethod
    def update_game_state(self, game):
        raise NotImplementedError()

class AttackMoveResult(MoveResult):
    
    def __init__(self, move_result_dictionary, attack_move):
        """Takes the results from the given attack move and creates a result object."""
        super().__init__(move_result_dictionary)
        self.attackers_lost = int(move_result_dictionary['_content']['return']['_content']['results']['totalattackerlosses'])
        self.defenders_lost = int(move_result_dictionary['_content']['return']['_content']['results']['totaldefenderlosses'])
        if 'captured' in move_result_dictionary['_content']['return']['_content']['results']:
            self.captured = move_result_dictionary['_content']['return']['_content']['results']['captured'] != '0'
        else:
            self.captured = False
        if 'eliminate' in move_result_dictionary['_content']['return']['_content']['results']:
            self.defender_eliminated  = move_result_dictionary['_content']['return']['_content']['results']['eliminate'] != '0'
        else:
            self.defender_eliminated = False
        self.from_territory = attack_move.from_territory
        self.to_territory = attack_move.to_territory
        self.defending_player = attack_move.to_territory.owner
    
    def update_game_state(self, game):
        """Update the game state from the attack. This involves updating the army counts and updating
        the defending territory owner if it was captured."""
        self.from_territory.armies -= self.attackers_lost
        self.to_territory.armies -= self.defenders_lost
        
        if self.captured:
            self.to_territory.owner = self.from_territory.owner
            
            if 'freetransfer' in self.possible_actions:
                self.from_territory.armies = self.from_territory.armies - 3
                self.to_territory.armies = 3
            else:
                self.to_territory.armies = self.from_territory.armies - 1 
                self.from_territory.armies = 1
                
            if self.defender_eliminated:
                self.defending_player.active = False
                 

class PlaceUnitsMoveResult(MoveResult):
    
    def __init__(self, move_result_dictionary, place_units_move):
        super().__init__(move_result_dictionary)
        self.territories_dict = place_units_move.territory_dict
        
    def update_game_state(self, game):
        """Update the board state by updating the number of armies on each territory after placing."""
        for territory, armies in self.territories_dict.items():
            territory.armies += armies

class FreeTransferMoveResult(MoveResult):
    
    def __init__(self, move_result_dictionary, free_transfer_move):
        super().__init__(move_result_dictionary)
        self.moved_units = free_transfer_move.number_of_armies
        
    def update_game_state(self, game):
        #The last move should be an attack move. If the last move is None then that means
        #the bot was started on the free transfer phase and does not have enough information
        #to update the board state.
        if game.last_move != None:
            game.last_move.from_territory.armies -= self.moved_units
            game.last_move.to_territory.armies += self.moved_units

move_result_constructors = dict(attack=AttackMoveResult,
                                placeunits=PlaceUnitsMoveResult,
                                freetransfer=FreeTransferMoveResult) 

def process_move_result(move_result_dictionary, move, game):
    """After taking a move Warfish returns information about that move as json. This takes
    that information as a dictionary and transforms it into a MoveResult object. It also updates
    the board state based on the move results."""
    result = None
    constructor = move_result_constructors.get(move.action_id)
    if constructor:
        result = constructor(move_result_dictionary, move)
        result.update_game_state(game)
    else:
        result = move_result_dictionary
    return result

        
if __name__ == "__main__":
    import doctest
    doctest.testmod()