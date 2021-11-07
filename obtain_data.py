import numpy as np


def generate_groups(stops, seats, seed=0):
    """
    Obtains the amount of stops, seats and the seed (default = 0) to create 
    the groups that want to board the bus. The group size is chossen from a
    uniform distribution. The start stop is choosen first and then the end
    stop. This selection does not create a uniform distribution of group sizes.
    It creates more smaller groups than bigger groups. Alternatively, 
    (commented out) I can create a uniform distribution of group sizes, but 
    then the start stop is not uniform distributed and tends to have bigger 
    groups. In both cases, the problem is that at the beggining of the route
    there are empty seats since there are not enough demand. The demand for 
    both cases is high in the middle of the route, and lower towards the edges.
    """

    np.random.seed(seed)
    
    # Creats arrays to select from
    group_sizes = np.arange(10)+1
    ride_lengths = np.arange(stops)[1:]

    max_capacity = seats*stops
    
    groups= []
    route_capacity = 0
    # Iterates while there is still in avarage enough capacity in the bus.
    # The maximum capacity is increased by 5% to have to reject groups.
    while route_capacity <= max_capacity*1.05:
        # Selects a random size from a unifrom distribution of group sizes
        g_size = np.random.choice(group_sizes, 1)[0]
        
        # Selects a ride length from a uniform distribution and starting stop
        # from a uniform distribution of possible starting points
        # ride_len = np.random.choice(ride_lengths,1)[0]
        # start = np.random.choice(stops-ride_len, 1)[0]
        # end = start+ride_len    
        
        # Selects the starting stop from a unifrom distribution and the
        # end stop from a uniform distribution from the remaining stops
        start = np.random.choice(stops-1, 1)[0]
        end = np.random.choice(np.arange(start+1,stops),1)[0]     
        
        # Update route capacity and append group to the list
        route_capacity +=g_size*(end-start)
        groups.append([start, end, g_size])
    
    return groups