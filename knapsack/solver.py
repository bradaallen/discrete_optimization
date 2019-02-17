#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import numpy as np
import time
Item = namedtuple("Item", ['index', 'value', 'weight'])

# we want to loop through all items

class dfs:
    
    def __init__(self, file_location):
        self.iterations = 0
        self.items, self.item_count, self.capacity = self._load_data(file_location)
        self.best_value = 0
        self.best_set = np.zeros(len(self.items)).astype(int)
        
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
                   
        for item in range(self.next_level, len(self.items), 1):
            # if we already have a best value that is higher than what is possible, break
            if self.current_max_value < self.best_value:
                break

            # if the next item leads us to go "over" in weight, break
            # otherwise, include and update state
            # if we are at the end of a branch, update
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
            
        self.floor, self.kept_value = self._update_floor_and_kept_value(items=self.items, 
                                                                        capacity=self.capacity, 
                                                                        level=self.current_level, 
                                                                        function_set=self.current_set.copy(),
                                                                        iterations=self.iterations)
        
        self.current_max_value = self._value_estimate(items=self.items, 
                                                        capacity=self.capacity, 
                                                        level=self.current_level, 
                                                        function_set=self.current_set.copy(), 
                                                        iterations=self.iterations)

        self.next_level = self.current_level + 1
        
        return self.current_max_value, self.floor, self.kept_value, self.next_level, self.current_set
        
    def _load_data(self, input_data):
    
        def density_sort(item_list):
            return(sorted(item_list, key=lambda item:-item.density))

        Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])

        # parse the input
        lines = input_data.split('\n')

        firstLine = lines[0].split()
        item_count = int(firstLine[0])
        capacity = int(firstLine[1])

        items = []

        for i in range(1, item_count+1):
            line = lines[i]
            parts = line.split()
            items.append(Item(i-1, int(parts[0]), int(parts[1]), float(parts[0])/float(parts[1])))

        items = density_sort(items)

        return items, item_count, capacity
    
    @staticmethod
    def _value_estimate(items, capacity, level, function_set, iterations):
    #This finds the best fractional value that the bag can hold. 
        
        starting_est = 0

        if iterations > 0:
            function_set[level] = 0
            function_set[level+1:] = 1

        for i, item in enumerate(items):
            if (item.weight < capacity) & (function_set[i] == 1):
                starting_est += item.value
                capacity -= item.weight
            elif function_set[i] == 0:
                pass
            else:
                return(starting_est + capacity*item.density)

        return starting_est
    
    @staticmethod
    def _update_floor_and_kept_value(items, capacity, level, function_set, iterations):
    #This finds the best fractional value that the bag can hold. 
        
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

def _load_data(input_data):
    
    Item = namedtuple("Item", ['index', 'value', 'weight', 'density'])

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1]), float(parts[0])/float(parts[1])))
    
    return items, item_count, capacity

def _build_table(items, item_count, capacity):
    
    dp_table = np.zeros(shape=(capacity + 1, item_count + 1))

    for j in range(item_count):
        item = items[j]
        for i in range(capacity + 1):
            current_weight = item.weight
            current_value = item.value

            value_if_include = 0
            prior_knapsack_at_weight = dp_table[i, j]

            if current_weight <= i:
                prior_knapsack_if_included = dp_table[max(i-current_weight, 0), j]
                value_if_include = prior_knapsack_if_included + current_value

            if value_if_include > prior_knapsack_at_weight:
                dp_table[i, j+1] = value_if_include
            else:
                dp_table[i, j+1] = prior_knapsack_at_weight
    
    return dp_table

def _generate_output(dp_table, items, item_count, capacity):

    # choose the best items
    taken = [0]*item_count
    current_item = item_count
    current_capacity = capacity
    prior_item = current_item - 1

    value = int(dp_table[current_capacity, current_item])

    for current_item in range(current_item, 0, -1):
        # current item is included
        if dp_table[current_capacity, current_item] != dp_table[current_capacity, prior_item]:
            taken[current_item-1] = 1

            current_capacity = current_capacity - items[current_item-1].weight
            current_item = prior_item
            prior_item = current_item - 1

        # current item is not included, move over one spot
        else:
            current_item = prior_item
            prior_item = current_item - 1

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    
    return output_data
def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    items, item_count, capacity = _load_data(input_data)

    try:
        dp_table = _build_table(items, item_count, capacity)
        output_data = _generate_output(dp_table, items, item_count, capacity)
        return output_data

    except:
        testobj = dfs(file_location=input_data)
        testobj.explore_branch()

        first_time = time.time()
        second_time = time.time()
        
        # exhaust
        while (np.sum(testobj.current_set) > 0) & (second_time - first_time < 300):
            testobj.explore_branch()
            second_time = time.time()

        # sort "back" the selected items
        index_list = []
        for i, item in enumerate(testobj.items):
            index_list.append(testobj.items[i].index)
            
        zipped_list = zip(index_list, testobj.best_set)
        resorted_selection = sorted(list(zipped_list), key=lambda x: x[0])
        final_selection = [y for (x, y) in resorted_selection]
        
        # prepare the solution in the specified output format
        output_data = str(testobj.best_value) + ' ' + str(0) + '\n '
        output_data += ' '.join(map(str, final_selection))
        return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

