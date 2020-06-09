"""
Test for dummy lockdown vector
"""

from os.path import dirname, join
from help_project.src.exitstrategies.interface import ExitStrategies


def test_strat_dict():
    pass_test = False
    print_output_files = False

    # Generate strategies dictionary
    exit_strat = ExitStrategies()
    strat_dict = exit_strat.get_exit_strategies()

    for strat_id in strat_dict:
        # Check for zero rows or columns
        strat_df = strat_dict[strat_id]
        if (strat_dict[strat_id].shape[0] == 0) or (strat_dict[strat_id].shape[1] == 0):
            pass_test = False
            break

        # Print to file if required
        if print_output_files:
            folder_name = dirname(dirname(__file__))
            folder_name = join(join(folder_name, "exitstrategies"), "output")
            file_name = strat_id + "_output.csv"
            file_path = join(folder_name, file_name)
            strat_df.to_csv(file_path)

        # Set flag to pass test
        pass_test = True

    assert pass_test
