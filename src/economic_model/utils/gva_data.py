"""
file to get the gva data for india
"""
from os import path
import pandas as pd


class BaseGVA():
    """
    class for Base GVA
    """
    def __init__(self):
        dir_path = path.dirname(path.realpath(__file__))
        gva_df = pd.read_csv(dir_path + "/../data/gva_data.csv")
        gva_df = gva_df.loc[~gva_df['2019'].isna()]
        gva_df = gva_df.set_index("Industry")
        self.gva_mapping = gva_df['2019'].to_dict()

    def get_gvas(self):
        """
        simply return the base GVA,
        in the future this would be a statistical model
        """
        return self.gva_mapping
