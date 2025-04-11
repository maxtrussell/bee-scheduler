# Bee Scheduler

Allows for setting rates for arbitrary blocks of time in [Beeminder](https://www.beeminder.com)a.

## Usage

To use this library, two environment variables need to be set first:
```bash
$ export BEEMINDER_USER="<beeminder username>"
$ export BEEMINDER_TOKEN="<beeminder api token"
```

This information may be found at https://www.beeminder.com/api/v1/auth_token.json

To schedule a break (rate=0) for the weekend of April 19th to April 20th:
```python
from bee_scheduler.scheduler import schedule_rate

start = date(year=2025, month=4, day=19)
end = date(year=2025, month=4, day=20)
rate = 0
schedule_rate(goal_name, start, end, rate)
```
