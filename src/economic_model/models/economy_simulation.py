from __future__ import division  # makes division work correctly
import random
from builtins import range
from help_project.src.economic_model.models.firm import Firm
from help_project.src.economic_model.models.household import Household
from abcEconomics import Simulation
import pandas as pd
import numpy as np
import sys,os
""" 
1. declares the timeline
2. build one Household agent representing all the households and one Firm each for each sector
3. For every labor_endowment an agent has gets one trade or usable labor per round. If it is not used at the end of the round it disaapears.
4. Firms' and Households' possesions are monitored ot the points marked in timeline.
"""

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

# blockPrint()
def main(parameters, agent_parameters, labor_alphas, shocks_to_labor_supply):
    simulation = Simulation(processes=1)

    firms = simulation.build_agents(
        Firm, 'firm', num_sectors = len(agent_parameters), agent_parameters=agent_parameters)
    households = simulation.build_agents(
        Household, 'household', number=1, firms_info=agent_parameters, labor_alphas = labor_alphas[0], needed_labor = labor_alphas[1])


    for rnd in range(parameters['rounds']):
        if rnd>5:
            # for i in range(number_sectors):
                # enablePrint()
                # print(firms[i].last_output)
                # blockPrint()
            households.apply_shocks(shocks_to_labor_supply)
        simulation.advance_round(rnd)
        households.create_labor()
        households.sell_labor()
        firms.buy_labor()
        firms.production()
        firms.panel_log(goods=['money', 'GOOD_sector1', 'GOOD_sector2'],
                        variables=['last_output'])
        firms.quotes()
        households.buy_goods()
        firms.buy_goods()
        firms.sell_goods()
        households.panel_log(goods=['money', 'GOOD_sector1', 'GOOD_sector2'],
                           variables=['current_utility'])
        households.consumption()
        firms.adjust_target()
        # firms.adjust_price()
    simulation.finalize()
    firms = pd.read_csv(simulation.path +'/panel_firm.csv')
    shocks = []
    for i in range(len(agent_parameters)):
        temp_firms = firms.loc[firms['name']=='firm'+str(i)]
        shocks.append(temp_firms['last_output'].iloc[-1]/temp_firms['last_output'].iloc[0])
    return shocks

def comma_convert(stri):
    return float(stri.replace(",", ""))

def series_convert(series):
    return series.apply(comma_convert)

def series_normalize(series):
    return (series / np.sum(series.iloc[:-1]))


def simulate_economy(shocks_to_labor_supply=None):
    parameters = {'name': '2x2',
                  'random_seed': None,
                  'rounds': 500,}

    # Cleaning input output table for india
    india_input_output = pd.read_csv(os.path.dirname(__file__) + '/../data/india_input.csv')
    india_input_output.columns = india_input_output.iloc[0]
    india_input_output = india_input_output.iloc[1:]
    india_input_output = india_input_output.set_index('To: (sector in column)')
    india_input_output = india_input_output.apply(series_convert)
    india_input_output.iloc[-2] = india_input_output.iloc[-2] + india_input_output.iloc[-4] + india_input_output.iloc[-5] +india_input_output.iloc[-6]
    india_input_output = india_input_output.drop(['TXS_IMP_FNL: Taxes less subsidies on intermediate and final products (paid in foreign countries)' , 'TXS_INT_FNL: Taxes less subsidies on intermediate and final products (paid in domestic agencies, includes duty on imported products)', 'TTL_INT_FNL: Total intermediate consumption at purchasers’ prices', 'TTL_97T98: Private households with employed persons'], axis = 0)
    india_input_output = india_input_output.drop(columns = india_input_output.columns[-8:])
    india_input_output = india_input_output.drop(columns = [india_input_output.columns[-2]])

    number_sectors = len(india_input_output)-2
    ratio_df = india_input_output.iloc[:,:-1].apply(series_normalize)
    labor_df = india_input_output.iloc[:-2,-1]/np.sum(india_input_output.iloc[:-2,-1])

    agent_parameters = []
    labor_dict = {}
    labor_requirement = 0
    for i in range(number_sectors):
        temp_dict = {}
        temp_dict['sector'] = 'sector'+str(i)
        ratio_dict = {}
        for j in range(number_sectors):
            if ratio_df.iloc[j,i] > 0.00001:
                ratio_dict['GOOD_sector'+str(j)] = ratio_df.iloc[j,i]
        ratio_dict['labor'] = ratio_df.iloc[number_sectors,i]
        temp_dict['ratio_dict'] = ratio_dict
        agent_parameters.append(temp_dict)
        labor_dict['GOOD_sector'+str(i)] = labor_df.iloc[i]

    output_input_ratio = [0]*number_sectors
    for i in range(number_sectors):
        for key in agent_parameters[i]['ratio_dict'].keys():
            if key=="labor":
                labor_requirement+=agent_parameters[i]['ratio_dict'][key]
                continue
            output_input_ratio[int(key.split('r')[-1])] += agent_parameters[i]['ratio_dict'][key]

    for key in labor_dict.keys():
        output_input_ratio[int(key.split('r')[-1])] += labor_dict[key]
    labor_alphas = [labor_dict, labor_requirement]
    for i in range(number_sectors):
        agent_parameters[i]['output_input_ratio']=output_input_ratio[i]
    shocks_array=[]
    for i in range(len(india_input_output)-2):
        if india_input_output.index[i] in shocks_to_labor_supply.keys():
            shocks_array.append(0.5 + 0.5*(shocks_to_labor_supply[india_input_output.index[i]]))
        else:
            shocks_array.append(1)
    shocks_to_labor_supply = shocks_array
    if shocks_to_labor_supply is None:
        shocks_to_labor_supply = [random.uniform(0.5,1) for i in range(number_sectors)]
    shocks =  main(parameters,agent_parameters,labor_alphas, shocks_to_labor_supply)
    GVAs={}
    for i in range(number_sectors):
        GVAs[india_input_output.index[i]]=(shocks[i]*india_input_output.iloc[-1,i])
    return GVAs

