#!/usr/bin/env python3
"""Five fixed caption inputs. Run before and after a prompt change."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path

# Set before importing the adapter or tools.
os.environ['AI201_CACHE'] = '0'
import config
config.CACHE_ENABLED = False
from tools import create_fit_card
from utils.data_loader import load_listings

CASES = [
    ('lst_001', 'Pair the jeans with a white ribbed tank top and chunky white sneakers.', ['white ribbed tank top', 'chunky white sneakers']),
    ('lst_002', 'Pair the tee with wide-leg khaki trousers and a brown leather belt.', ['wide-leg khaki trousers', 'brown leather belt']),
    ('lst_003', 'Layer the flannel over a black fitted turtleneck and finish with black combat boots.', ['black fitted turtleneck', 'black combat boots']),
    ('lst_004', 'Wear the track jacket with charcoal joggers and white canvas sneakers.', ['charcoal joggers', 'white canvas sneakers']),
    ('lst_005', 'Pair the corduroy pants with a cream cable-knit sweater and brown suede ankle boots.', ['cream cable-knit sweater', 'brown suede ankle boots']),
]
RULE = ('PASS if the caption recommends at least one listed companion piece, retaining its color and clothing type; '
        'equivalent wording is allowed. Generic advice such as neutral colors does not count. '
        'Target: at least 4 of 5. Score manually and quote supporting words. '
        'This additional check does not replace original criterion 4.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', required=True, choices=['before', 'after'])
    args = parser.parse_args()
    listings = {item['id']: item for item in load_listings()}
    cases = [dict(new_item=listings[item_id], outfit=outfit, details=details)
             for item_id, outfit, details in CASES]
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    folder = config.RESULTS_DIR / f'caption_details_{stamp}_{args.label}'
    folder.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).resolve().parent / 'tools.py'
    evidence = {'label': args.label, 'cache_enabled': config.CACHE_ENABLED,
                'rule': RULE, 'tools_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'inputs_sha256': hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest(),
                'trials': []}
    # Save the exact tool implementation used, for reproducibility.
    (folder / 'tools_snapshot.py').write_bytes(source.read_bytes())
    def save():
        (folder / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding='utf-8')
        lines = [f'# Caption detail check — {args.label}', '', RULE, '',
                 'Caching disabled. Outputs below are unedited. Verdicts await review.', '']
        for i, trial in enumerate(evidence['trials'], 1):
            lines += [f'## Trial {i}', '', 'Source: tools.py::create_fit_card', '',
                      '```json', json.dumps(trial, ensure_ascii=False, indent=2), '```', '',
                      '**Verdict and supporting quotation:** Pending review.', '']
        (folder / 'report.md').write_text('\n'.join(lines), encoding='utf-8')
    save()
    for i, case in enumerate(cases, 1):
        print(f'Caption {i}/5 (cache disabled)', flush=True)
        trial = dict(case)
        try:
            trial['caption'] = create_fit_card(case['outfit'], case['new_item'])
        except Exception as exc:
            trial['error'] = f'{type(exc).__name__}: {exc}'
        evidence['trials'].append(trial)
        save()
    print(f'Review: {folder / "report.md"}')


if __name__ == '__main__':
    main()
