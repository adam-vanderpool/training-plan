import os
import json
from datetime import datetime, date, timedelta
import garminconnect

GARMIN_EMAIL    = os.environ['GARMIN_EMAIL']
GARMIN_PASSWORD = os.environ['GARMIN_PASSWORD']

# Minimal plan representation mirroring WEEKS in index.html.
# Each entry: startDate (YYYY-MM-DD), week number, days (list of session lists per day Mon-Sun).
PLAN = [
    {
        'week': 1, 'startDate': '2026-03-09',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'run'}],
            [],
            [{'sport': 'swim'}],
            [{'sport': 'bike'}, {'sport': 'run'}],
        ],
    },
    {
        'week': 2, 'startDate': '2026-03-16',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 3, 'startDate': '2026-03-23',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 4, 'startDate': '2026-03-30',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 5, 'startDate': '2026-04-06',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 6, 'startDate': '2026-04-13',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 7, 'startDate': '2026-04-20',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 8, 'startDate': '2026-04-27',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 9, 'startDate': '2026-05-04',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}, {'sport': 'run'}],
            [],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 10, 'startDate': '2026-05-11',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}, {'sport': 'run'}],
            [],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 11, 'startDate': '2026-05-18',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}, {'sport': 'run'}],
            [],
            [{'sport': 'bike'}, {'sport': 'run'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 12, 'startDate': '2026-05-25',
        'days': [
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
        ],
    },
    {
        'week': 13, 'startDate': '2026-06-01',
        'days': [
            [{'sport': 'run'}],
            [{'sport': 'swim'}],
            [{'sport': 'bike'}],
            [{'sport': 'run'}],
            [],
            [{'sport': 'swim'}],
            [{'sport': 'race'}],
        ],
    },
]

# Map Garmin activity typeKey values → canonical sport names
SPORT_MAP = {
    'cycling':               'bike',
    'road_biking':           'bike',
    'mountain_biking':       'bike',
    'gravel_cycling':        'bike',
    'indoor_cycling':        'bike',
    'virtual_ride':          'bike',
    'running':               'run',
    'trail_running':         'run',
    'treadmill_running':     'run',
    'indoor_running':        'run',
    'lap_swimming':          'swim',
    'open_water_swimming':   'swim',
    'pool_swimming':         'swim',
}


def fmt_duration(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f'{h}:{m:02d}:{s:02d}'
    return f'{m}:{s:02d}'


def compute_pace(sport, duration_sec, distance_m):
    if duration_sec <= 0 or distance_m <= 0:
        return None
    if sport == 'swim':
        secs_per_100m = duration_sec * 100 / distance_m
        m = int(secs_per_100m // 60)
        s = int(secs_per_100m % 60)
        return f'{m}:{s:02d}/100m'
    if sport == 'run':
        secs_per_km = duration_sec * 1000 / distance_m
        m = int(secs_per_km // 60)
        s = int(secs_per_km % 60)
        return f'{m}:{s:02d}/km'
    if sport == 'bike':
        kmh = distance_m / duration_sec * 3.6
        return f'{kmh:.1f} km/h'
    return None


def find_plan_week(activity_date):
    """Return (week_entry, day_offset) or (None, None)."""
    for week in PLAN:
        start = date.fromisoformat(week['startDate'])
        end   = start + timedelta(days=6)
        if start <= activity_date <= end:
            return week, (activity_date - start).days
    return None, None


def main():
    client = garminconnect.Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login()

    end_date   = date.today()
    start_date = date(2026, 3, 9)  # plan start date

    raw = client.get_activities_by_date(
        start_date.isoformat(),
        end_date.isoformat(),
    )

    # Track which plan sessions are already matched: {(week_num, day_idx, session_idx)}
    matched_slots = set()

    activities = []
    unmatched  = []

    for act in raw:
        type_key     = (act.get('activityType') or {}).get('typeKey', '')
        sport        = SPORT_MAP.get(type_key)
        duration_sec = act.get('duration', 0) or 0
        distance_m   = act.get('distance', 0) or 0

        # Parse date from startTimeLocal ("2026-03-09 07:30:00")
        start_raw = act.get('startTimeLocal', '')
        try:
            activity_date = date.fromisoformat(start_raw[:10])
        except ValueError:
            continue

        pace = compute_pace(sport, duration_sec, distance_m) if sport else None

        base = {
            'date':         activity_date.isoformat(),
            'sport':        sport or type_key,
            'duration_sec': int(duration_sec),
            'distance_m':   int(distance_m),
            'pace':         pace,
        }

        if not sport:
            base['note'] = f'Unrecognized type: {type_key}'
            unmatched.append(base)
            continue

        week_entry, day_offset = find_plan_week(activity_date)
        if week_entry is None:
            base['note'] = 'Outside plan date range'
            unmatched.append(base)
            continue

        day_sessions = week_entry['days'][day_offset]
        matched_session = None
        for sess_idx, sess in enumerate(day_sessions):
            key = (week_entry['week'], day_offset, sess_idx)
            if sess['sport'] == sport and key not in matched_slots:
                matched_session = sess_idx
                matched_slots.add(key)
                break

        if matched_session is None:
            base['note'] = 'No planned session this day'
            unmatched.append(base)
            continue

        activities.append({
            **base,
            'matched_week':    week_entry['week'],
            'matched_day':     day_offset,
            'matched_session': matched_session,
        })

    output = {
        'generated':  datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'activities': activities,
        'unmatched':  unmatched,
    }

    with open('actuals.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f'Wrote actuals.json: {len(activities)} matched, {len(unmatched)} unmatched')


if __name__ == '__main__':
    main()
