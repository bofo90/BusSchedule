from obtain_data import generate_groups
from model_schedule import maximize_income
from result_analysis import present_results

stops = 20  # <= 20
seats = 30  # <= 30
proportional_ticket = True
seed = 0

groups_list = generate_groups(stops, seats, seed)

boarding_groups, total_passengers, seats_info = maximize_income(stops, seats, 
                                                            groups_list, 
                                                            proportional_ticket)

present_results(boarding_groups, seats_info, stops, seats, seed, total_passengers, proportional_ticket)
