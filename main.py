from obtain_data import generate_groups
from model_schedule import maximize_income
from result_analysis import present_results

"""
This program received a list of groups that want to board a bus route, 
indicating when the groups hops in, hops out and the amount of people the 
group has. Then it creates a schedule of the groups by maximazing the income
from the tickets. The tiket cost can be proportional to the distance travel
(proportional_ticket = True) or just a fixed value per person (proportional_
ticket = False). 

First the program creates a random list of groups with diferent sizes, 
starting and ending stop. It then creates a schedule of the groups and returns 
a list mentioning if the groups board or not. Finally it creates two plots.
The first one shows the occupancy of the seats in the bus while the second 
plots all the groups with colors depending if they board or not.

stops = amount of stops of the bus route.
seats = amount of seats that the bus has.
proportional_ticket = boolean that changes the price of the ticket.
seed = seed of the random generator.

group_list = list of groups with the numbers being: start stop, end stop and
             amount of passengers.
             
boarding_groups = same list as group_list but as a pandas DataFrame with a 
                  column showing if the group boards or not the bus
total_passengers = total amount of passengers that board the bus
seats_info = pandas DataFrame that contains how the seats in the bus are being
             occupied byt the different groups along the route

"""

stops = 20  # <= 20
seats = 30  # <= 30
proportional_ticket = True
seed = 0

groups_list = generate_groups(stops, seats, seed)

boarding_groups, total_passengers, seats_info = maximize_income(stops, seats, 
                                                            groups_list, 
                                                            proportional_ticket)

present_results(boarding_groups, seats_info, stops, seats, seed, total_passengers, proportional_ticket)
