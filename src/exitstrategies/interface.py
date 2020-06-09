"""
Interface class to be used by other modules
"""

from help_project.src.exitstrategies.data_elt import DataELT


class ExitStrategies():
    # TODO: Update these
    focus_areas_eco = ["agriculture", "chemical", "commerce", "construction", "education", "fin_prof_services",
                       "food_consumables", "healthcare", "hospitality_tourism", "manufacturing", "mining",
                       "engineering", "media", "energy", "telecom", "public_admin", "supply_chain_ship",
                       "forest_husb_fish", "textiles", "transportation", "utilities"]
    # TODO: Update these
    focus_areas_soc = ["gathering_size", "open_border", "air_travel", "roal_rail_travel", "public_transport", "curfew",
                       "ecommerce", "contact_tracing", "covid_testing"]

    def __init__(self):
        pass

    def get_exit_strategies(self):
        data_elt = DataELT()
        exit_strategies = data_elt.extract_data()
        # TODO: parameterize start_date, end_date, start_day (numerical day since day 1), end_day, format (df/array/map)
        return exit_strategies

    def get_focus_areas(self):
        focus_areas = self.focus_areas_eco.extend(self.focus_areas_soc)
        return focus_areas

    def get_focus_areas_eco(self):
        return self.focus_areas_eco

    def get_focus_areas_soc(self):
        return self.focus_areas_soc
