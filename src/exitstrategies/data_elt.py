"""
Class for ELT of data files
"""

from os import listdir
from os.path import dirname, join
import datetime
import pandas as pd


class DataELT():

    def __init__(self):
        pass

    def extract_data(self):
        strat_dict = {}

        # Get data folder and start_date
        start_date = self.convert_to_date("2020_02_29")
        project_root = dirname(dirname(__file__))
        data_folder = join(join(project_root, "exitstrategies"), "data")
        file_list = listdir(data_folder)

        # Fetch list of available strategies
        for file_name in file_list:
            if ".csv" in file_name:
                # Load file
                file_path = join(data_folder, file_name)
                file_df = pd.read_csv(file_path, encoding="utf-8")

                # Create list of dates
                date_array = file_df.columns.values
                date_list = [date_value for date_value in date_array if date_value != date_array[0]]
                date_list.sort()

                # Save dataframe to dict
                ld_df = self.create_lockdown_df(file_df, date_list, start_date)
                strat_df = ld_df.transpose()
                strat_id = file_name.replace(".csv", "")
                strat_dict[strat_id] = strat_df

        return strat_dict

    def convert_to_date(self, date_str):
        date_items = date_str.split("_")
        date_value = datetime.datetime(int(date_items[0]), int(date_items[1]), int(date_items[2]))
        return date_value

    def create_lockdown_df(self, file_df, date_list, start_date):
        # Create base dataframe
        ld_df = file_df.drop(date_list, axis=1)
        day0_values = [1] * ld_df.shape[0]
        prev_date = start_date

        for date_str in date_list:
            # Perform date calcs
            impl_date = self.convert_to_date(date_str)
            day_count_since_prev = (impl_date - prev_date).days
            day_count_till_prev = (prev_date - start_date).days

            # Update dataframe with same column for previous lockdown period
            for i in range(day_count_since_prev):
                if day_count_till_prev == 0:
                    ld_df[str(day_count_till_prev + i)] = day0_values
                else:
                    ld_df[str(day_count_till_prev + i)] = file_df[prev_date_str]

            # Update prev_date
            prev_date = impl_date
            prev_date_str = date_str

        # Update index as column names to prevent wrong index in subsequent transpose operation (see extract_data())
        ld_cols = ld_df.columns.values
        ld_df.set_index(ld_cols[0], inplace=True)

        return ld_df
