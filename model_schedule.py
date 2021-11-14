import numpy as np
import pandas as pd

import result_analysis as resan

def maximize_income(stops, seats, groups_list, proportional_ticket = False):
    """
    It takes the group list and generates first a pandas DataFrame to analyze 
    the results. Then it creates a schedule of the bus assuming it has
    infinite amount of seats to allocate all groups. For this it uses an 
    interval partitioning algorithm. Then it transforms the schedule to a 
    matrix form representing the seats and stops. From the matrix it removes
    the lowest income seats together with the full group and tries to 
    realocate all the groups that have been removed. Finally it transforms
    back the matrix from into a list of seats for easy plot and calculates the
    total amount of passengers in the route.
    """
 
    groups, ord_groups = create_dataframe(groups_list)
    
    resan.simple_all_groups(groups, stops, 'All groups')
    
    all_seats = create_interval_partitioning(ord_groups)
    resan.simple_schedule(all_seats, stops, 'Infinite bus')
    
    seat_matrix = seats_to_matrix(all_seats, stops)
    seat_matrix_red, seat_cost, groups = remove_low_income_seats(
        seat_matrix, groups, seats, proportional_ticket
        )
    
    seats_info = matrix_to_seats(seat_matrix_red, stops)
        
    total_passengers = groups['passengers'][groups['boards']].sum()
    
    return groups, total_passengers, seats_info

def create_dataframe(groups_list):
    """
    Creates DataFrame from list in order to have esay access to all information
    """
    
    groups = np.zeros((len(groups_list),5), dtype=int)
    groups = pd.DataFrame(np.array(groups_list), columns = ['start', 'end', 'passengers'])
    groups.index.names = ['group_id']
    groups.reset_index(inplace = True)
    groups['boards'] = True
    ord_groups = groups.sort_values(by=['start','end'])  
    
    return groups, ord_groups


def create_interval_partitioning(ord_groups):
    """
    It takes the groups ordered by the startting stop and then finishin stop.
    It starts adding the groups to the schedule to the available seats. If the
    bus has no seats available it adds more seats so all groups can board the 
    bus. It returns a list of seats occupancy, where it says for each seat
    and eah group when the groups hops in and hops out
    """
    
    # Creates a list with enough seats (total number of passengers)
    last_occ_seats = np.zeros(np.sum(ord_groups['passengers']))
    seats_num = np.arange(np.sum(ord_groups['passengers']))
    
    all_seats = np.empty((0,4))
    # Iterates theough all the groups
    for i, g in ord_groups.iterrows():
        # Checks which seat is empty when the group want to board
        all_av_seats = last_occ_seats<=g['start']
        # Select first available seats according the the amount of passengers
        best_seats = seats_num[all_av_seats][:g['passengers']]
        # Update the occupancy for the selected seats
        last_occ_seats[best_seats] = g['end'] 
        
        # Creates list specifing the info of the occupancy
        seats_relation = np.concatenate(([best_seats],
                                         [np.ones(np.size(best_seats))*g['start']],
                                         [np.ones(np.size(best_seats))*g['end']],
                                         [np.ones(np.size(best_seats))*i]),
                                        axis=0).transpose()
        all_seats = np.concatenate((all_seats,seats_relation),axis=0)
    
    # Creates DataFrame from numpy array
    all_seats = pd.DataFrame(all_seats, columns=['seat_id', 'start', 'end',
                                                 'group_id'], dtype=int)
    
    return all_seats

def seats_to_matrix(all_seats, stops):
    """
    Transforms from the seat information array to a matrix form where each
    row represents a seat and each column a stop. 
    """
    
    seats_num = np.size(np.unique(all_seats['seat_id']))
    
    seat_matrix = np.zeros((seats_num,stops), dtype=int)-1
    for _, s in all_seats.iterrows():
        seat_matrix[s['seat_id'], s['start']:s['end']] = s['group_id']
            
    return seat_matrix

def matrix_to_seats(seat_matrix_red, stops):
    """
    Transfroms from a matrix form to a seat infromation array.
    """
    
    seats_num = np.shape(seat_matrix_red)[0]
    stops_arr = np.arange(stops)
    
    red_seats = np.empty((0,4))
    # Iterates through all the seats
    for s in range(seats_num):
        groups_in_seat = np.unique(seat_matrix_red[s,:])
        # Itrates through all the groups in the specified seat
        for g in groups_in_seat[1:]:
            here = seat_matrix_red[s,:]==g
            red_seats = np.concatenate((red_seats,[[s, stops_arr[here][0], 
                                                    stops_arr[here][-1]+1,
                                                    g]]),
                                       axis = 0)     
    
    red_seats = pd.DataFrame(red_seats, columns=['seat_id', 'start', 'end',
                                                 'group_id'], dtype=int) 
    red_seats.sort_values(by=['seat_id','start']).reset_index(drop=True)

    return red_seats

def remove_low_income_seats(seat_matrix, groups, seats, proportional_ticket):
    """
    To remove the lowest income rows, it first calculates the icome of each
    row. Then removes from the lowest income seat up until the amount of seats
    are the specidied one or smaller.
    """
    
    seat_cost = calculate_seat_cost(seat_matrix, proportional_ticket)

    while np.shape(seat_matrix)[0] > seats:
        seat_matrix, groups = remove_seats(seat_matrix, seat_cost, groups)
        seat_cost = calculate_seat_cost(seat_matrix, proportional_ticket)
    
    return seat_matrix, seat_cost, groups
        
def calculate_seat_cost(seat_matrix, proportional_ticket):
    """
    It calculates the income per seat. The income depends on the ticket price,
    that can be propoetional to the length of the ride or just a fixed price.
    """
    
    if proportional_ticket:
        # Income is propoettional to the total amount of time that the seat is
        # occupied
        seat_cost = np.sum((seat_matrix > -1), axis = 1)
    else:
        # Income is proportional to the amount of different groups that board
        # the seats
        df = pd.DataFrame(seat_matrix.T)
        seat_cost = df.nunique().values-1
    
    return seat_cost

def remove_seats(seat_matrix, seat_cost, groups):
    """
    To remove the lowest income seat, the algorithm is divided in 3:
        First, it localizes the lowest income seat, obtains the groups that 
        are there sitted and removes all the passengers of these groups in the 
        bus. 
        Second, it removes the empty seats, reducing the size of the bus.
        Third, it loops through all the rejected groups and try to realocate 
        them in the bus since empty seats may be available for them.
    
    Returns the reduces seat-stop matrix
    
    """
    
    # Localize the lowest income seat and the groups that are seated in it
    low_income_seat = seat_cost.argmin()
    groups_in_seat = np.unique(seat_matrix[low_income_seat,:])[1:]
    
    # Remove entire group seating in the seat
    for g in groups_in_seat:
        seat_matrix[seat_matrix == g] = -1
        groups.loc[g,'boards'] = False
    
    # Remove the empty seats from the bus
    empty_seats = (seat_matrix == -1).all(axis=1)
    seat_matrix = seat_matrix[~empty_seats,:]
    
    # Realocate groups to the bus if possible
    elim_groups = groups['group_id'][groups['boards']==False].values
    av_seats = np.arange(np.shape(seat_matrix)[0])
    for g in elim_groups:
        pos_seats = (seat_matrix[:,groups['start'][g]:groups['end'][g]]==-1).all(axis=1)
        if np.sum(pos_seats)>=groups['passengers'][g]:
            seats_to_occ = av_seats[pos_seats][:groups['passengers'][g]]
            seat_matrix[seats_to_occ,groups['start'][g]:groups['end'][g]] = g
            groups.loc[g,'boards'] = True
    
    return seat_matrix, groups