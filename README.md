# Bee Scheduler

Allows for setting rates for arbitrary blocks of time in [Beeminder](https://www.beeminder.com).

## Usage

This library may be installed using pip:
```bash
$ pip install bee-scheduler
```

To use this library, you will need your Beeminder username and auth token, which can be found at https://www.beeminder.com/api/v1/auth_token.json.

To schedule a break (rate=0) for the day of April 20th:
```python
from datetime import date

from bee_scheduler.scheduler import BeeScheduler

scheduler = BeeScheduler("<your beeminder username>", "<your beeminder auth token>")

start = date(year=2025, month=4, day=20)
end = date(year=2025, month=4, day=20)
rate = 0
scheduler.schedule_rate(goal_name, start, end, rate)
```

And here you can see the resulting break scheduled in a beeminder graph:
![graph with break](https://files.maxtrussell.net/share/3e251cf9-a9bd-48c9-b705-d0cebc131493)
