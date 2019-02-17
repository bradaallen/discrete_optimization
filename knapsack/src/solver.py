#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import time
from depth_first import dfs
from dynamic_prog import dp

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    try:
        check_output = dp(file_location=input_data)
        output_data = check_output.dynamic_programming_algo()
        return output_data

    except:
        testobj = dfs(input_data=input_data)
        testobj.explore_branch()

        first_time = time.time()
        second_time = time.time()
        
        # exhaust
        while np.sum(testobj.current_set) > 0 & (second_time - first_time < 300):
            testobj.explore_branch()
            second_time = time.time()
        
        output_data = testobj._generate_output()

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

