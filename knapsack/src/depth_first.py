'''Brad Allen. Scratch work.'''

import pandas as pd
import os
from collections import namedtuple
import numpy as np

class dfs:
    '''This class employs a depth first search strategy - the main function is explore_branch(),
       which will traverse a branch until it:
           (1) uses up too much weight (the "floor" is negative), 
           (2) is exhausted, or 
           (3) does not have the potential to have more value than the current best answer.
           
        The state of the next branch for exploring is calculated using the next_branch() function,
        which updates the next node for searching, as well as the starting floor and max potential
        value.'''
    
    def __init__(self, input_data):
        '''As the algo traverses different branches, many variables are required to keep state - 
           for global values as well as updating nodes to explore.'''
        
        # global variables
        self.input_data = input_data
        self.iterations = 0
        self.items, self.item_count, self.capacity = self._load_data()
        self.best_value = 0
        self.best_set = np.zeros(len(self.items)).astype(int)
        
        # node-specific variables - "kept_value" is value accrued, "floor" is weight left
        self.kept_value = 0
        self.floor = self.capacity
        
        self.current_set = np.zeros(len(self.items)).astype(int)
        self.current_level = 0
        self.max_potential_value = self._value_estimate(items=self.items, 
                                                        capacity=self.capacity, 
                                                        level=self.current_level, 
                                                        function_set=np.ones(len(self.items)).astype(int), 
                                                        iterations=self.iterations)
        self.current_max_value = self.max_potential_value
        self.next_level = self.current_level
    
    def explore_branch(self):
        '''Traverses an individual branch until it:
           (1) uses up too much weight (the "floor" is negative), 
           (2) is exhausted, or 
           (3) does not have the potential to have more value than the current best answer.
           
           Then updates state for next exploration. This function is used in a while loop.
           '''
        
        for item in range(self.next_level, len(self.items), 1):
            # if we already have a best value that is higher than what is possible, break
            if self.current_max_value < self.best_value:
                break

            # if the next item leads us to go "over" in weight, break otherwise, include 
            # and update state. If we are at the end of a branch, update
            if self.items[item].weight <= self.floor:
                self.kept_value += self.items[item].value
                self.floor -= self.items[item].weight
                self.current_set[item] = 1  

                if self.kept_value > self.best_value:
                    self.best_value = self.kept_value
                    self.best_set = self.current_set.copy()    

            # when we go over from weight, update state and break
            else:
                break
                
        self.iterations += 1
        
        return self.best_value, self.best_set, self.iterations, self.next_branch(item)
    
    def next_branch(self, item):
        '''Updates state values for next branch to be traversed. Calculates:
           (1) max_potential_value
           (2) floor
           (3) kept_value
           (4) index_level and item set'''
        
        # update floor and max_potential_value
        if item == len(self.items) - 1: # branch exhausted
            if self.current_set[0] == 1:  
            # find first 0, set level to one higher and that value to 0
                self.current_level = np.where(self.current_set == 0)[0][0] - 1                
                self.current_set[self.current_level] = 0
                self.current_set[item] = 1
                
            else:
                # find first 1, set value to 0 and make current level; subsequent levels to 1
                self.current_level = np.where(self.current_set == 1)[0][0]                
                self.current_set[self.current_level] = 0
                self.current_set[self.current_level+1:] = 1
        else:
            self.current_level = item
        
        # calculate floor and kept value
        self.floor, self.kept_value = self._update_floor_and_kept_value(items=self.items, 
                                                                        capacity=self.capacity, 
                                                                        level=self.current_level, 
                                                                        function_set=self.current_set.copy(),
                                                                        iterations=self.iterations)
        # calculate max value
        self.current_max_value = self._value_estimate(items=self.items, 
                                                        capacity=self.capacity, 
                                                        level=self.current_level, 
                                                        function_set=self.current_set.copy(), 
                                                        iterations=self.iterations)

        self.next_level = self.current_level + 1
        
        return self.current_max_value, self.floor, self.kept_value, self.next_level, self.current_set
        
    @staticmethod
    def _value_estimate(items, capacity, level, function_set, iterations):
        '''This finds the best fractional value that the bag can hold.'''
        
        # initialize. since this is an update, it is called when branches
        # "move left" - therefore, the current level will be 0 (item not included)
        estimated_value = 0
        if iterations > 0:
            function_set[level] = 0
            function_set[level+1:] = 1
        
        # for new branch, calculate potential/fractional value creation
        for i, item in enumerate(items):
            if (item.weight < capacity) & (function_set[i] == 1):
                estimated_value += item.value
                capacity -= item.weight
            elif function_set[i] == 0:
                pass
            else:
                return(estimated_value + capacity*item.density)

        return estimated_value
    
    @staticmethod
    def _update_floor_and_kept_value(items, capacity, level, function_set, iterations):
        '''This finds the floor and "starting value" for the node in the new branch.''' 
        
        # initialize. set later values to 0 - this allows us to loop through the 
        # branch fully without accounting for those items' value
        floor = capacity
        kept_value = 0
        if iterations > 0:
            function_set[level] = 0
            function_set[level+1:] = 0

        for i, item in enumerate(items):
            if (item.weight < capacity) & (function_set[i] == 1):
                floor -= item.weight
                kept_value += item.value
            elif function_set[i] == 0:
                pass

        return floor, kept_value
    
    def _load_data(self):
        '''Takes Coursera input files splits them, and creates a tuple in 
        their preferred format. Sorted - needs to be unsorted for output.'''
    
        def density_sort(item_list):
            return(sorted(item_list, key=lambda item:-item.density))

        Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])

        # parse the input
        lines = self.input_data.split('\n')

        firstLine = lines[0].split()
        item_count = int(firstLine[0])
        capacity = int(firstLine[1])

        items = []

        for i in range(1, item_count+1):
            line = lines[i]
            parts = line.split()
            items.append(Item(i-1, int(parts[0]), int(parts[1]), 
                              float(parts[0])/float(parts[1])))

        items = density_sort(items)

        return items, item_count, capacity
    
    def _generate_output(self):
        '''Since we sorted the output to improve the runtime, we need to resort
           it back to the original value for grading.'''
        
        # sort "back" the selected items
        index_list = []
        for i, item in enumerate(self.items):
            index_list.append(self.items[i].index)
            
        zipped_list = zip(index_list, self.best_set)
        resorted_selection = sorted(list(zipped_list), key=lambda x: x[0])
        final_selection = [y for (x, y) in resorted_selection]
        
        # prepare the solution in the specified output format
        output_data = str(self.best_value) + ' ' + str(0) + '\n '
        output_data += ' '.join(map(str, final_selection))
        
        return output_data