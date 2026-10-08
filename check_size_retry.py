#!/usr/bin/env python3
"""Record fixed size-mismatch queries before and after the retry change."""
import argparse
import contextlib
import copy
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
from unittest.mock import patch

os.environ['AI201_CACHE'] = '0'
import config
config.CACHE_ENABLED = False
import agent
from tools import search_listings
from utils.data_loader import get_example_wardrobe

CASES = [
    ('graphic tee', 'XXS', 30),
    ('flannel', 'XXS', 30),
    ('track jacket', 'XXS', 50),
    ('corduroy', 'XXS', 40),
    ('jeans', 'XXS', 50),
]
TARGET = ('At least 4 of 5 recover a listing after exactly one retry removing only size, '
          'with a clear size-relaxation notice. All recovered listings remain within budget '
          'and the selected item reaches the outfit tool unchanged. '
          'Original acceptance criteria remain unchanged.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', choices=['before', 'after'], required=True)
    args = parser.parse_args()
    # Validate every fixture before making model calls. Do not silently substitute queries.
    fixtures = []
    for description, size, price in CASES:
        inputs = dict(description=description, size=size, max_price=price)
        strict = search_listings(**inputs)
        relaxed = search_listings(description, None, price)
        if strict or not relaxed:
            raise ValueError(f'Invalid fixture: {inputs}; strict={len(strict)}, relaxed={len(relaxed)}. Stop and review the dataset.')
        fixtures.append(dict(query=f'{description} under ${price}, size {size}',
                             inputs=inputs, strict_results=strict, relaxed_results=relaxed))
    folder = config.RESULTS_DIR / ('size_retry_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f') + '_' + args.label)
    folder.mkdir(parents=True, exist_ok=False)
    for name in ['agent.py', 'tools.py', 'mcp_server.py']:
        (folder / (name[:-3] + '_snapshot.py')).write_bytes((config.ROOT / name).read_bytes())
    evidence = dict(label=args.label, target=TARGET, cache_enabled=False,
                    fixtures_sha256=hashlib.sha256(json.dumps(fixtures, sort_keys=True).encode()).hexdigest(),
                    trials=[])
    original_call = agent.call_tool
    original_outfit = agent.suggest_outfit
    def save():
        (folder / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
        text = ['# Size-retry check — ' + args.label, '', TARGET, '',
                'Five distinct fixed size-mismatch queries; not a general success-rate estimate.',
                'Caching disabled. Review notices in stdout/session and call arguments before assigning verdicts.', '']
        for i, trial in enumerate(evidence['trials'], 1):
            text += [f'## Trial {i}', '', '```json', json.dumps(trial, ensure_ascii=False, indent=2), '```', '', '**Verdict:** Pending review.', '']
        (folder / 'report.md').write_text('\n'.join(text), encoding='utf-8')
    save()
    for i, fixture in enumerate(fixtures, 1):
        print(f'Size-retry trial {i}/5', flush=True)
        trial = copy.deepcopy(fixture)
        trial.update(mcp_calls=[], outfit_inputs=[])
        def capture_call(name, arguments):
            entry = dict(name=name, arguments=copy.deepcopy(arguments))
            trial['mcp_calls'].append(entry)
            result = original_call(name, arguments)
            entry['returned'] = copy.deepcopy(result)
            return result
        def capture_outfit(item, wardrobe):
            trial['outfit_inputs'].append(copy.deepcopy(dict(new_item=item, wardrobe=wardrobe)))
            return original_outfit(item, wardrobe)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            try:
                with patch.object(agent, 'call_tool', side_effect=capture_call), patch.object(agent, 'suggest_outfit', side_effect=capture_outfit):
                    trial['session'] = agent.run_agent(fixture['query'], get_example_wardrobe())
            except Exception as exc:
                trial['error'] = f'{type(exc).__name__}: {exc}'
        trial['stdout'] = stdout.getvalue()
        evidence['trials'].append(trial)
        save()
    print(f'Review: {folder / "report.md"}')


if __name__ == '__main__':
    main()
