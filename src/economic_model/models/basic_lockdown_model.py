"""
This defines a very basic economic model, this is going to change in the future
"""
from typing import Dict
import attr
import os
import numpy as np
import pandas as pd
from help_project.src.economic_model.utils import gva_data
from help_project.src.exitstrategies import lockdown_policy as lockdown
from help_project.src.economic_model.models.economy_simulation import simulate_economy


class EconomicLockdownModel():
    """
    Class for basic Economic lockdown model, this just multiplies the
    base GVA(from last quarter) with the lockdown vector (productivity)
    of a sector
    """

    def __init__(self, country=None):
        self.country = country

    def _get_economic_vector_for_single_policy(self, lockdown_policy: lockdown.LockdownPolicy):
        lockdown_policy = attr.asdict(lockdown_policy)
        gva = gva_data.BaseGVA()
        sector_mappings = gva.get_sector_mapping()
        sector_mappings = sector_mappings.dropna()
        mapping_dict = {}
        for i in range(len(sector_mappings)):
            if sector_mappings.iloc[i]['sector'] not in mapping_dict:
                mapping_dict[sector_mappings.iloc[i]['sector']] = \
                    [sector_mappings.iloc[i]['lockdown_sector']]
            else:
                mapping_dict[sector_mappings.iloc[i]['sector']].append(
                    sector_mappings.iloc[i]['lockdown_sector'])

        baseline_gva = gva.get_gvas()
        india_input_output = pd.read_csv(os.path.dirname(__file__) + '/../data/india_input.csv')
        india_input_output.columns = india_input_output.iloc[0]
        india_input_output = india_input_output.iloc[1:]
        india_input_output = india_input_output.set_index('To: (sector in column)')
        india_input_output = india_input_output.drop(
            ['TXS_IMP_FNL: Taxes less subsidies on intermediate and final products (paid in foreign countries)',
             'TXS_INT_FNL: Taxes less subsidies on intermediate and final products (paid in domestic agencies, includes duty on imported products)',
             'TTL_INT_FNL: Total intermediate consumption at purchasers’ prices',
             'TTL_97T98: Private households with employed persons'], axis=0)
        india_input_output = india_input_output.drop(columns=india_input_output.columns[-8:])
        india_input_output = india_input_output.drop(columns=[india_input_output.columns[-2]])
        sectors = india_input_output.index.values[:-2]
        labor_shocks = {}
        for sector in sectors:
            labor_shocks[sector]=1
        for key in mapping_dict:
            if key not in sectors:
                continue
            weights = []
            for sector in mapping_dict[key]:
                if sector in lockdown_policy:
                    weights.append(lockdown_policy[sector])
            if len(weights) > 0:
                labor_shocks[key] = np.mean(weights)
        adjusted_gvas = simulate_economy(labor_shocks)
        return adjusted_gvas

    def get_economic_vector(
            self, lockdown_policy: lockdown.LockdownTimeSeries) -> Dict[str, float]:
        """Compute the economic output of applying a given policy.

        Args:
            lockdown_policy: Time-series of policies to use.

        Returns:
            A dictionary containing adjusted GVA for different sectors.
        """
        output = {}
        for policy_application in lockdown_policy.policies:
            policy_output = self._get_economic_vector_for_single_policy(
                policy_application.policy)
            for key, value in policy_output.items():
                if key not in output:
                    output[key] = 0
                output[key] = value / 365 / 4 * len(policy_application)
        return output
