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

"""This module is for processing the results from getHistory into objects."""

import abc

"""Abstract base class for each move in the history."""
class HistoryMove(metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def __init__(self, id, unix_timestamp, player_id):
        self.id = id
        self.unix_timestamp = unix_timestamp
        self.player_id = player_id
    
    @abc.abstractproperty
    def result_id(self):
        """The id of the move as it appears when getting the history."""
        raise NotImplementedError()
    
"""The results from a past attack."""
class AttackHistoryMove(HistoryMove):

    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.border_mods = history_move_dictionary['m'] #m stands for border_mod, but I have no idea what that means
        self.attackers_lost = history_move_dictionary['al']
        self.defenders_lost = history_move_dictionary['dl']
        self.from_territory_id = history_move_dictionary['fcid']
        self.to_territory_id = history_move_dictionary['tcid']
        self.attack_dice = history_move_dictionary['ad']
        self.defend_dice = history_move_dictionary['dd']
        self.defending_player_id = history_move_dictionary['ds']
        
    @property
    def result_id(self):
        return 'a'

"""Describes a territory being captured."""
class CaptureHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.captured_territory_id = history_move_dictionary['cid']
        self.captured_player_id = history_move_dictionary['ds']

    @property
    def result_id(self):
        return 'c'

"""Describes a player being eliminated."""
class EliminatePlayerHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.eliminated_player_id = history_move_dictionary['es']

    @property
    def result_id(self):
        return 'e'

"""Describes a new game that is created."""
class CreateNewGameHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.log_version = history_move_dictionary['logver']
        
    @property
    def result_id(self):
        return 'n'
    
"""Move for when a user joins a game."""
class JoinGameHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        
    @property
    def result_id(self):
        return 'j'
    
"""Assigns a player a seat position."""
class AssignSeatPositionHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        
    @property
    def result_id(self):
        return 'o'

"""Start the Game"""
class StartGameHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], None)
        
    @property
    def result_id(self):
        return 's'

"""Territory selected as a neutral territory."""
class NeutralTerritorySelectHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        
    @property
    def result_id(self):
        return 'y'

"""Bonus units received."""
class BonusUnitsHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.bonus_units = history_move_dictionary['num']
        
    @property
    def result_id(self):
        return 'z'
    
"""A territory was selected."""
class SelectTerritoryHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.territory_id = history_move_dictionary['cid']
        
    @property
    def result_id(self):
        return 't'

"""Units were placed on a territory."""
class PlaceUnitHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.territory_id = history_move_dictionary['cid']
        self.num_units = history_move_dictionary['num']
        
    @property
    def result_id(self):
        return 'p'

"""Units were transferred."""
class TransferHistoryMove(HistoryMove):

    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.from_territory_id = history_move_dictionary['fcid']
        self.to_territory_id = history_move_dictionary['tcid']
        self.num_units = history_move_dictionary['num']
        
    @property
    def result_id(self):
        return 'f'    

"""A card was awarded at the end of a turn."""
class AwardedCardHistoryMove(HistoryMove):

    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.card_id = history_move_dictionary['clist']
        
    @property
    def result_id(self):
        return 'g'
    
"""A set of cards was turned in."""
class UseCardsHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.used_cards = history_move_dictionary['clist']
        self.awarded_units = history_move_dictionary['num']
        
    @property
    def result_id(self):
        return 'u'

"""Cards were captured from a player."""
class CaptureCardsHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        self.used_cards = history_move_dictionary['clist']
        self.number_of_cards = history_move_dictionary['num']
        self.cards_captured_from_id = history_move_dictionary['ds']
        
    @property
    def result_id(self):
        return 'h'

"""The game was won."""
class WinHistoryMove(HistoryMove):
    
    def __init__(self, history_move_dictionary):
        super().__init__(history_move_dictionary['id'], history_move_dictionary['t'], history_move_dictionary['s'])
        
    @property
    def result_id(self):
        return 'w'    

history_constructors = dict(a=AttackHistoryMove,
                            c=CaptureHistoryMove,
                            e=EliminatePlayerHistoryMove,
                            f=TransferHistoryMove,
                            g=AwardedCardHistoryMove,
                            h=CaptureCardsHistoryMove, 
                            j=JoinGameHistoryMove,
                            n=CreateNewGameHistoryMove,
                            o=AssignSeatPositionHistoryMove,
                            p=PlaceUnitHistoryMove,
                            s=StartGameHistoryMove,
                            t=SelectTerritoryHistoryMove,
                            u=UseCardsHistoryMove,
                            w=WinHistoryMove,
                            y=NeutralTerritorySelectHistoryMove,
                            z=BonusUnitsHistoryMove)

"""Turn the move history from the Warfish api call into a dictionary of move HistoryMove objects."""
def process_history(move_dictionary):
    """Process a dictionary of moves returned by making the getHistory Warfish API call."""
    history = []
    for item in move_dictionary:
        try:
            history.append(history_constructors[item['a']](item))
        except KeyError:
            print('{0} is not implemented yet. {1}'.format(item['a'], item))
    return history
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()