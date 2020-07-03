"""Visualization module.

Wraps an optimizer with visualizations for displaying on a notebook."""
import random
from typing import Dict
from typing import List
from typing import Optional

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from help_project.src.disease_model import data
from help_project.src.optimization import loss_function


class Visualization:
    """Visualization around an optimizer."""

    @classmethod
    def plot(cls, title, x_label, y_label, size=(12, 4)):
        """Create a plot."""
        # pylint: disable=invalid-name
        _, ax = plt.subplots(figsize=size)
        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        return ax

    @classmethod
    def pareto(cls, pareto_frontier: List[loss_function.Result], **kwargs):
        """Plot the pareto frontier."""
        # pylint: disable=invalid-name
        values = sorted(result.loss for result in pareto_frontier)
        x, y = zip(*values)

        plot_kwargs = {
            'marker': 'o',
            'linestyle': 'dashed',
            'color': 'purple',
        }
        plot_kwargs.update(kwargs)
        plt.plot(x, -np.array(y), **plot_kwargs)

    @classmethod
    def plot_samples(cls,
                     results: List[loss_function.Result],
                     n: Optional[int] = None,
                     **kwargs):
        """Plot sample points."""
        # pylint: disable=invalid-name
        if n is not None:
            results = random.sample(results, n)

        plot_kwargs = {
            'marker': 'o',
            'color': 'blue',
            'linestyle': 'none',
        }
        plot_kwargs.update(kwargs)
        x, y = zip(*[result.loss for result in results])
        plt.plot(x, -np.array(y), **plot_kwargs)

    @classmethod
    def plot_health_timeseries(
            cls,
            attributes: List[str],
            past_data: data.HealthData,
            predictions: Dict[str, data.HealthData],
            ground_truth: Optional[data.HealthData] = None):
        """Plot the health timeseries.

        Args:
            attributes: List of attributes of the health data to plot.
            past_data: The past health data.
            predictions: A dictionary of predictions for different policies.
            ground_truth: The optional ground truth for the future health data.
        """
        def inner_plot(
                title,
                past_data: pd.Series,
                predictions: Dict[str, pd.Series],
                ground_truth: Optional[pd.Series] = None):
            # pylint: disable=invalid-name,too-many-locals
            past_df = pd.DataFrame({'date': past_data.index.strftime('%Y-%m-%d'),
                                    'past': past_data})
            future_data = {}
            for name, pred in predictions.items():
                future_data['date'] = pred.index.strftime('%Y-%m-%d')
                future_data[name] = pred
            if ground_truth is not None:
                future_data['ground_truth'] = ground_truth
            future_df = pd.DataFrame(future_data)
            df = pd.concat([past_df, future_df])
            dates = df['date']

            melt = df.melt(id_vars=['date'],
                           var_name='data',
                           value_name='value')
            ax = cls.plot(title, 'date', 'value')
            ax.set_xticklabels(labels=dates, rotation=45, ha='right')
            sns.pointplot(x='date', y='value', data=melt, hue='data')
            good_tick_count = 15
            if len(dates) > good_tick_count:
                n = len(dates) // good_tick_count
                for ind, label in enumerate(ax.get_xticklabels()):
                    label.set_visible(ind % n == 0)  # every nth label is kept
            return ax

        for attribute in attributes:
            inner_plot(
                attribute,
                getattr(past_data, attribute),
                {name: getattr(val, attribute) for name, val in predictions.items()},
                getattr(ground_truth, attribute)
            )
