#!/usr/bin/env python3
import json

data = json.load(open('event_data.json'))
events = data['events']

print('All events with "Just" or "Closer":')
matching_events = [e for e in events if 'Just' in e.get('event_text', '') or 'Closer' in e.get('event_text', '')]

for i, e in enumerate(matching_events):
    event_text = e.get('event_text', '')
    choices = e.get('detected_choices', 'N/A')
    made = e.get('choice_made', 'N/A')
    print(f'  {i+1}. "{event_text}" -> choices: {choices}, made: {made}')

print(f'\nTotal events found: {len(matching_events)}')
