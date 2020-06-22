"""
Class for ELT of data files
"""

from os import listdir
from os.path import dirname, join
import datetime
import pandas as pd

from help_project.src.exitstrategies import lockdown_policy


class DataELT():

    @classmethod
    def extract_attribute_data(cls):
        strat_dict = {}

        # Get data folder and start_date
        start_date = DataELT.convert_to_date("2020_02_29")
        data_folder = join(dirname(__file__), "data")
        file_list = listdir(data_folder)

        # Fetch list of available strategies
        for file_name in file_list:
            if ".csv" in file_name:
                # Load file
                file_path = join(data_folder, file_name)
                file_df = pd.read_csv(file_path, encoding="utf-8").set_index("focus_area")

                # Create list of dates
                date_columns = sorted(file_df.columns)
                dates = [DataELT.convert_to_date(d) for d in date_columns]
                dates.append(None)

                policy_applications = []
                if dates[0] > start_date:
                    default_policy = lockdown_policy.LockdownPolicy(
                        **dict(zip(file_df.index, [0] * len(file_df.index))))
                    policy_applications.append(lockdown_policy.LockdownPolicyApplication(
                        policy=default_policy,
                        start=start_date,
                        end=dates[0],
                    ))

                for i, date_col in enumerate(date_columns):
                    policy_applications.append(lockdown_policy.LockdownPolicyApplication(
                        policy=lockdown_policy.LockdownPolicy(**dict(file_df[date_col])),
                        start=dates[i],
                        end=dates[i + 1],
                    ))

                strat_id = file_name.replace(".csv", "")
                strat_dict[strat_id] = lockdown_policy.LockdownTimeSeries(policy_applications)

        return strat_dict

    @classmethod
    def convert_to_date(cls, date_str):
        return datetime.datetime.strptime(date_str, '%Y_%m_%d').date()
