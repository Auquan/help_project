"""Data structures for lockdown policies."""
import datetime
from typing import Optional
from typing import Sequence
from typing import Union
import attr


@attr.s(frozen=True)
class LockdownPolicy:  # pylint: disable=too-few-public-methods
    """Struct for holding a parameter."""
    # TODO (Should we keep defaults here? They might hide errors)

    # Economic focus
    agriculture: float = attr.ib(default=0.0)
    chemical: float = attr.ib(default=0.0)
    commerce: float = attr.ib(default=0.0)
    construction: float = attr.ib(default=0.0)
    education: float = attr.ib(default=0.0)
    fin_prof_services: float = attr.ib(default=0.0)
    food_consumables: float = attr.ib(default=0.0)
    healthcare: float = attr.ib(default=0.0)
    hospitality_tourism: float = attr.ib(default=0.0)
    manufacturing: float = attr.ib(default=0.0)
    mining: float = attr.ib(default=0.0)
    engineering: float = attr.ib(default=0.0)
    media: float = attr.ib(default=0.0)
    energy: float = attr.ib(default=0.0)
    telecom: float = attr.ib(default=0.0)
    public_admin: float = attr.ib(default=0.0)
    supply_chain_ship: float = attr.ib(default=0.0)
    forest_husb_fish: float = attr.ib(default=0.0)
    textiles: float = attr.ib(default=0.0)
    transportation: float = attr.ib(default=0.0)
    utilities: float = attr.ib(default=0.0)

    # Social focus
    gathering_size: float = attr.ib(default=0.0)
    open_border: float = attr.ib(default=0.0)
    air_travel: float = attr.ib(default=0.0)
    roal_rail_travel: float = attr.ib(default=0.0)
    public_transport: float = attr.ib(default=0.0)
    curfew: float = attr.ib(default=0.0)

    ecommerce: float = attr.ib(default=0.0)
    events_allowed: float = attr.ib(default=0.0)
    worship_allowed: float = attr.ib(default=0.0)

    contact_tracing: float = attr.ib(default=0.0)
    covid_testing: float = attr.ib(default=0.0)


@attr.s(frozen=True)
class LockdownPolicyApplication:  # pylint: disable=too-few-public-methods
    """Struct for holding a lockdown policy along with its application period."""
    policy: LockdownPolicy = attr.ib()
    start: datetime.datetime = attr.ib()
    end: Optional[datetime.datetime] = attr.ib()

    def __len__(self) -> int:
        if self.end is not None:
            return (self.end - self.start).days
        raise ValueError('The given policy has no end date')


@attr.s(frozen=True)
class LockdownTimeSeries:  # pylint: disable=too-few-public-methods
    """Struct for holding a lockdown time series."""
    policies: Sequence[LockdownPolicyApplication] = attr.ib()

    def __len__(self) -> int:
        return sum(len(policy) for policy in self.policies)

    def _date_with_offset(self, offset):
        return self.policies[0].start + datetime.timedelta(days=offset)

    def __getitem__(self, key):
        if not self.policies:
            raise IndexError('Empty lockdown time series does not support slicing')

        # Implementation of slicing
        if isinstance(key, slice):
            if key.step is not None:
                raise IndexError('Slicing a lockdown time series does not support a step size.')
            start = (self._date_with_offset(key.start)
                     if isinstance(key.start, int)
                     else key.start)
            end = (self._date_with_offset(key.stop)
                   if isinstance(key.stop, int)
                   else key.stop)
            policies_in_range = [
                policy
                for policy in self.policies
                if (policy.start < end and
                    (policy.end is None or policy.end > start))
            ]

            return LockdownTimeSeries(
                policies=[
                    LockdownPolicyApplication(
                        policy=p.policy,
                        start=max(start, p.start),
                        end=min(end, p.end) if p.end else end,
                    ) for p in policies_in_range])

        # Retrieving by index uses it as an offset from the start date
        if isinstance(key, int):
            key = self._date_with_offset(key)

        # Retrieve by date
        print(key)
        for policy in self.policies:
            if policy.start <= key and (policy.end is None or policy.end > key):
                return policy.policy
        raise IndexError('Given index not found in time series')
