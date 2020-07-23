from typing import TypedDict, Dict, List, Any
from prometheus_client.parser import text_fd_to_metric_families, Sample

clients = [
    'lighthouse',
    'prysm',
    'teku',
    'nimbus',
    'lodestar',
]

class Entry(TypedDict):
    doc: Dict[str, str]
    type: Dict[str, str]
    labels: Dict[str, Dict[str, List[str]]]

entries: Dict[str, Entry] = {}


for client in clients:
    with open(f'client_data/{client}.txt', 'rt') as f:
        for family in text_fd_to_metric_families(f):
            if family.name not in entries:
                entries[family.name] = Entry(
                    doc={},
                    type={},
                    labels={},
                )
            entry = entries[family.name]
            entry['doc'][client] = family.documentation
            entry['type'][client] = family.type
            entry_labels = entry['labels']
            if client not in entry_labels:
                entry_labels[client] = {}
            sample: Sample
            for sample in family.samples:
                for k, v in sample.labels.items():
                    if k not in entry_labels[client]:
                        entry_labels[client][k] = []
                    if v in entry_labels[client][k]:
                        continue
                    if len(v) < 6 or len(entry_labels[client][k]) == 0:
                        entry_labels[client][k].append(v)

print("entry count", len(entries))

for k, v in entries.items():
    if len(v['doc']) > 1:
        print(k, v['doc'].keys())

import json

with open('comparison.json', 'w') as f:
    print(json.dump(entries, f, indent='  ', sort_keys=True))

