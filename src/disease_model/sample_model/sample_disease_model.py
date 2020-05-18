'''
This file is simply a placeholder used to set up the repository, the interfaces etc
are not indicative of the actual models to be built.
'''
import pandas as pd


def get_cases(country):
    """ Sample function to get the number of cases for a country """
    cases_df = pd.read_csv('data/full_data.csv')
    cases_df = cases_df[cases_df['location'] == country]
    return cases_df[['date', 'location', 'total_cases']]
