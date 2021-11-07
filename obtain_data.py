import numpy as np


def generate_groups(stops, seats, seed=0):
    
    # groupsize <= 10
    
    np.random.seed(seed)
    
    group_sizes = np.arange(10)+1
    max_capacity = seats*stops
    ride_lengths = np.arange(stops)[1:]
    
    groups= []
    route_capacity = 0
    while route_capacity <= max_capacity*1.05:
        g_size = np.random.choice(group_sizes, 1)[0]
        # ride_len = np.random.choice(ride_lengths,1)[0]
        # start = np.random.choice(stops-ride_len, 1)[0]
        # end = start+ride_len    
        start = np.random.choice(stops-1, 1)[0]
        end = np.random.choice(np.arange(start+1,stops),1)[0]        
        route_capacity +=g_size*(end-start)
        groups.append([start, end, g_size])
    
    return groups