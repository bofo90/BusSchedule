import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as matl

def cm2inch(value):
    return value/2.54

def NiceGraph2D(axes, nameX, nameY, mincoord = [np.NaN, np.NaN], maxcoord = [np.NaN, np.NaN], divisions = [np.NaN, np.NaN],buffer = [0.0, 0.0, 0.0]):
    
    gray = '0.2'
    matl.rcParams.update({'font.size': 12})

    if ~np.isnan(mincoord[0]) and ~np.isnan(maxcoord[0]):
        axes.set_xlim([mincoord[0]-buffer[0], maxcoord[0]+buffer[0]])
        if isinstance(divisions[0], (list, tuple, np.ndarray)):
            if ~np.isnan(divisions[0]).any():
                axes.set_xticks(divisions[0])
        else:
            if ~np.isnan(divisions[0]):
                axes.set_xticks(np.linspace(mincoord[0],maxcoord[0],divisions[0]))
    axes.set_xlabel(nameX,labelpad=0, color = gray)
    
    if ~np.isnan(mincoord[1]) and ~np.isnan(maxcoord[1]):
        axes.set_ylim([mincoord[1]-buffer[1], maxcoord[1]+buffer[1]])
        if isinstance(divisions[1], (list, tuple, np.ndarray)):
            if ~np.isnan(divisions[1]).any():
                axes.set_yticks(divisions[1])
        else:
            if ~np.isnan(divisions[1]):
                axes.set_yticks(np.linspace(mincoord[1],maxcoord[1],divisions[1]))
    axes.set_ylabel(nameY,labelpad=0, color = gray)
   
    axes.xaxis.label.set_color(gray)
    axes.tick_params(axis='x', colors=gray, direction = 'in', width = 0.4)
    axes.yaxis.label.set_color(gray)
    axes.tick_params(axis='y', colors=gray, direction = 'in', width = 0.4)
    axes.tick_params(pad = 2)
    
    axes.tick_params(axis='y', which='minor', colors=gray, direction = 'in', width = 0.4)
    axes.tick_params(axis='x', which='minor', colors=gray, direction = 'in', width = 0.4)
    
    for axis in ['top','bottom','left','right']:
        axes.spines[axis].set_linewidth(0.4)
        axes.spines[axis].set_color(gray)
        
    return

def present_results(boarding_groups, seats_info, stops, seats, seed, total_passengers, proportional_tickets):
    
    plt.close('all')
    plot_schedule(seats_info, seats, stops, seed, proportional_tickets)
    
    plot_all_groups(boarding_groups, seats, stops, seed, proportional_tickets)
    
    # # Group size distribution
    # fig3 = plt.figure()
    # ax3 = plt.subplot(111)
    # for i, g in enumerate((boarding_groups['end']-boarding_groups['start']).sort_values()):
    #     ax3.plot([0,g],[i,i])
        
    # # Seat demand
    # fig4 = plt.figure()
    # ax4 = plt.subplot(111)
    # demand = np.arange(stops-1)
    # for i in np.arange(stops-1):
    #     demand[i] = boarding_groups['passengers'][(
    #         boarding_groups['start']<=i) & (boarding_groups['end']>i)].sum() 
    # ax4.plot(demand)
    

    
    # fig1.savefig(f'Results/Graph_{np.shape(all_points)[0]}points_{alpha}alpha_{seed}seed.pdf', transparent = True)
    
    
    return

def plot_schedule(seats_info, seats, stops, seed, proportional_tickets):
    
    fig1 = plt.figure()
    ax1 = plt.subplot(111)
    ax1.set_axis_off()

    groups = np.unique(seats_info['group_id'])
    colors = plt.cm.BrBG(np.linspace(0,1,np.size(groups)))

    for _ , s in seats_info.iterrows():
        this_c = colors[groups==s['group_id'],:]
        ax1.plot([s['start']+0.2,s['end']-0.2],[s['seat_id'],s['seat_id']], 
                 c=this_c, linewidth=4)
        # ax1.scatter([s['start']+0.1,s['end']-0.1],[s['seat_id'],s['seat_id']], 
        #             c=this_c, marker='|', s=100)
    
    plt.tight_layout()
    fig1.savefig(f'Results/Schedule_{seats}seats_{stops}stops_{seed}seed_{proportional_tickets}propticket.pdf', transparent = True)

    return

def plot_all_groups(boarding_groups, seats, stops, seed, proportional_tickets):
    
    fig2 = plt.figure()
    ax2 = plt.subplot(111)
    ax2.set_axis_off()

    i = 0
    for _ , g in boarding_groups.sort_values(by=['start','end']).iterrows():
        if g['boards']:
            line1, = ax2.plot([g['start']+0.2,g['end']-0.2],[i,i], 
                              c='#005F73', linewidth=4)
        else:
            line2, = ax2.plot([g['start']+0.2,g['end']-0.2],[i,i],
                              c='#BB3E03', linewidth=4)
        i += 1
        
    ax2.legend([line1, line2], ['accepted', 'rejected'])
    plt.tight_layout()
    fig2.savefig(f'Results/AllGroups_{seats}seats_{stops}stops_{seed}seed_{proportional_tickets}propticket.pdf', transparent = True)

    return
        