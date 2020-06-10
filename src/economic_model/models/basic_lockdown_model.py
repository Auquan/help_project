"""
This defines a very basic economic model, this is going to change in the future
"""

from help_project.src.economic_model.utils.gva_data import BaseGVA


class EconomicLockdownModel():
    """
    Class for basic Economic lockdown model, this just multiplies the
    base GVA(from last quarter) with the lockdown vector (productivity)
    of a sector
    """

    def __init__(self, country=None, lockdown_vector=None):
        self.country = country
        self.lockdown_vector = lockdown_vector

    def get_economic_vector(self):
        """
        get the economic vector for a country
        """
        # TODO
        # use the lockdown vector while calculating new GVAs
        # not using because of not sure of the structure right now
        gva = BaseGVA()
        return gva.get_gvas()
