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

"""A game of Warfish is represented by a series of moves. This abstract base class
provides a simple interface for executing specific types of moves."""

"""Make an attack."""
class AttackMove:
    
    def __init__(self, from_territory, to_territory, number_of_units, is_continuous):
        self.from_territory = from_territory
        self.to_territory = to_territory
        self.number_of_units = number_of_units
        self.is_continuous = is_continuous
        
    @property
    def action_id(self):
        return 'attack'
    
    def to_query_string(self):
        """Create a query string containing the name of the move and its arguments."""
        query_string = '&action={0}'.format(self.action_id)
        query_string += '&fromcid={0}&tocid={1}&numunits={2}&continuous={3}'.format(self.from_territory.id, self.to_territory.id, self.number_of_units, '1' if self.is_continuous else '0')
        return query_string

"""Place units in blind-at-once unit placement during game setup or in unit 
placement phase during a turn-based play turn. """
class PlaceUnitsMove:
    
    def __init__(self, territory_dict):
        """A move to place units takes a list of territory ids and a matching list of the number of units to put onto each territory."""
        self.action_id = 'placeunits'
        self.territory_dict = territory_dict
    
    def to_query_string(self):
        query_string = '&action={0}'.format(self.action_id)
        territory_ids = {territory.id for territory in self.territory_dict.keys()}
        query_string += '&clist={0}'.format(','.join(territory_ids)) + '&ulist={0}'.format(','.join([str(value) for value in self.territory_dict.values()]))
        return query_string

"""Used during turn-based play. It allows you to move additional armies after a successful attack."""
class FreeTransferMove:
    
    def __init__(self, number_of_armies):
        """A move to place units takes a list of territory ids and a matching list of the number of units to put onto each territory."""
        self.number_of_armies = number_of_armies
    
    @property
    def action_id(self):
        return 'freetransfer'
    
    def to_query_string(self):
        return '&action={0}&numunits={1}'.format(self.action_id, self.number_of_armies)

"""Ends your turn."""
class EndTurnMove:
    
    def __init__(self):
        self.action_id = 'endturn'
    
    def to_query_string(self):
        return '&action={0}'.format(self.action_id)
        
if __name__ == "__main__":
    import doctest
    doctest.testmod()