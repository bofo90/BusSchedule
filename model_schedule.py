import numpy as np
import pandas as pd

from result_analysis import plot_schedule

def maximize_income(stops, seats, groups_list, proportional_ticket = False):
    
    groups = np.zeros((len(groups_list),5), dtype=int)
    groups = pd.DataFrame(np.array(groups_list), columns = ['start', 'end', 'passengers'])
    groups.index.names = ['group_id']
    groups.reset_index(inplace = True)
    groups['boards'] = True
    ord_groups = groups.sort_values(by=['start','end'])   
    
    all_seats = create_interval_partitioning(ord_groups)
    seat_matrix = seats_to_matrix(all_seats, stops)
    seat_matrix_red, seat_cost, groups = remove_low_income_seats(
        seat_matrix, groups, seats, proportional_ticket
        )
    
    seats_info = matrix_to_seats(seat_matrix_red, stops)
        
    total_passengers = groups['passengers'][groups['boards']].sum()
    
    return groups, total_passengers, seats_info


def create_interval_partitioning(ord_groups):
    
    last_occ_seats = np.zeros(np.sum(ord_groups['passengers']))
    seats_num = np.arange(np.sum(ord_groups['passengers']))
    
    all_seats = np.empty((0,4))
    for i, g in ord_groups.iterrows():
        all_av_seats = last_occ_seats<=g['start']
        best_seats = seats_num[all_av_seats][:g['passengers']]      #select first available seats
        last_occ_seats[best_seats] = g['end']            #update the last_occ_seat for the selected seats
        
        seats_relation = np.concatenate(([best_seats],
                                         [np.ones(np.size(best_seats))*g['start']],
                                         [np.ones(np.size(best_seats))*g['end']],
                                         [np.ones(np.size(best_seats))*i]),
                                        axis=0).transpose()
        all_seats = np.concatenate((all_seats,seats_relation),axis=0)
    
    all_seats = pd.DataFrame(all_seats, columns=['seat_id', 'start', 'end',
                                                 'group_id'], dtype=int)
    
    return all_seats

def seats_to_matrix(all_seats, stops):
    
    seats_num = np.size(np.unique(all_seats['seat_id']))
    
    seat_matrix = np.zeros((seats_num,stops), dtype=int)-1
    for _, s in all_seats.iterrows():
        seat_matrix[s['seat_id'], s['start']:s['end']] = s['group_id']
            
    return seat_matrix

def matrix_to_seats(seat_matrix_red, stops):
    
    seats_num = np.shape(seat_matrix_red)[0]
    stops_arr = np.arange(stops)
    
    red_seats = np.empty((0,4))
    for s in np.arange(seats_num):
        groups_in_seat = np.unique(seat_matrix_red[s,:])
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
    
    seat_cost = calculate_seat_cost(seat_matrix, proportional_ticket)

    while np.shape(seat_matrix)[0] > seats:
        seat_matrix, groups = remove_seats(seat_matrix, seat_cost, groups)
        seat_cost = calculate_seat_cost(seat_matrix, proportional_ticket)
    
    return seat_matrix, seat_cost, groups
        
def calculate_seat_cost(seat_matrix, proportional_ticket):
    
    if proportional_ticket:
        seat_cost = np.sum((seat_matrix > -1), axis = 1)
    else:
        df = pd.DataFrame(seat_matrix.T)
        seat_cost = df.nunique().values-1
    
    return seat_cost

def remove_seats(seat_matrix, seat_cost, groups):
    
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
    for g in elim_groups:
        pos_seats = (seat_matrix[:,groups['start'][g]:groups['end'][g]]==-1).all(axis=1)
        if np.sum(pos_seats)>=groups['passengers'][g]:
            seats_to_occ = np.arange(np.shape(seat_matrix)[0])[pos_seats][:groups['passengers'][g]]
            seat_matrix[seats_to_occ,groups['start'][g]:groups['end'][g]] = g
            groups.loc[g,'boards'] = True
    
    return seat_matrix, groups