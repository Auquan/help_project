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
                       "ecommerce", "events_allowed", "worship_allowed", "contact_tracing", "covid_testing"]

    def __init__(self):
        pass

    def get_exit_strategies(self):
        exit_strategies = DataELT.extract_attribute_data()
        # TODO: parameterize start_date, end_date, start_day (numerical day since day 1), end_day, format (df/array/map)
        return exit_strategies

    @classmethod
    def get_focus_areas(cls):
        return ExitStrategies.focus_areas_eco + ExitStrategies.focus_areas_soc

    @classmethod
    def get_focus_areas_eco(cls):
        return ExitStrategies.focus_areas_eco

    @classmethod
    def get_focus_areas_soc(cls):
        return ExitStrategies.focus_areas_soc
