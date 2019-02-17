'''Brad Allen. Scratch work.'''

import pandas as pd
import os
from collections import namedtuple
import numpy as np

class dp:
    
    def __init__(self):
        self.input_data = input_data
    
    def dynamic_programming_algo(self):
        '''Generates a table for dynamic programming and infers output.
           Uses significant space and time O(k*n), but guaranteed optimal.'''
        
        # load the data
        items, item_count, capacity = self._load_data()

        # build the table
        dp_table = self._build_table(items, item_count, capacity)

        # generate output
        output_data = self._generate_output(dp_table, items, item_count, capacity)

        return output_data

    def _load_data(self):
        '''Takes Coursera input files splits them, and creates a tuple in 
           their preferred format. Unsorted.'''
        
        Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])

        # parse the input
        lines = self.input_data.split('\n')

        first_line = lines[0].split()
        item_count = int(first_line[0])
        capacity = int(first_line[1])

        items = []

        for i in range(1, item_count+1):
            line = lines[i]
            parts = line.split()
            items.append(Item(i-1, int(parts[0]), int(parts[1]), float(parts[0])/float(parts[1])))

        return items, item_count, capacity

    @staticmethod
    def _build_table(items, item_count, capacity):
        '''Create a table that is the capacity of the knapsack+1 and the number of items+1.
           For every item added, calculate the optimal solution at every capacity. This is
           done by iteratively building the table, and referring back to the prior optimal
           solution (ie. from the last item's solution).'''
        
        # initialize the table
        dp_table = np.zeros(shape=(capacity + 1, item_count + 1))

        for j in range(item_count):
            item = items[j]
            for i in range(capacity + 1):
                current_weight = item.weight
                current_value = item.value

                value_if_include = 0
                prior_knapsack_at_weight = dp_table[i, j]
                
                # determine what the weight would be if the new item is included
                if current_weight <= i:
                    prior_knapsack_if_included = dp_table[max(i-current_weight, 0), j]
                    value_if_include = prior_knapsack_if_included + current_value

                if value_if_include > prior_knapsack_at_weight:
                    dp_table[i, j+1] = value_if_include
                else:
                    dp_table[i, j+1] = prior_knapsack_at_weight

        return dp_table

    @staticmethod
    def _generate_output(dp_table, items, item_count, capacity):
        '''With the table output, determine the items that compose the optimal solution.
           This can be determined by reverse engineering the table (eg, if the "maximum value"
           was the same for a given capacity for the last item, the current item was not added.'''
        
        # initialize
        items_taken = [0]*item_count
        current_item = item_count
        current_capacity = capacity
        prior_item = current_item - 1
        optimal_value = int(dp_table[current_capacity, current_item])

        for current_item in range(current_item, 0, -1):
            # compare if max_value is different, determine if current item is included
            if dp_table[current_capacity, current_item] != dp_table[current_capacity, prior_item]:
                items_taken[current_item-1] = 1
                
                # reset for next iteration
                current_capacity = current_capacity - items[current_item-1].weight
                current_item = prior_item
                prior_item = current_item - 1

            # current item is not included, move over one spot
            else:
                current_item = prior_item
                prior_item = current_item - 1

        # prepare the solution in the specified output format
        output_data = str(optimal_value) + ' ' + str(0) + '\n'
        output_data += ' '.join(map(str, items_taken))

        return output_data