import json

with open('event_data.json', 'r') as f:
    data = json.load(f)

events = [e for e in data.get('events', []) if e.get('event_text', '') and 'Little Closer' in e['event_text']]
print(f'Found {len(events)} events:')
for e in events:
    print(f'- "{e["event_text"]}" -> choices: {e.get("detected_choices", "N/A")}, made: {e.get("choice_made", "N/A")}')
