#!/usr/bin/env python3
"""Record five trials per original criterion. PASS/FAIL decisions stay manual.
Run: python run_eval.py --label before
Persistence trials use an isolated temporary data directory, never your save.
"""
import argparse
import contextlib
import copy
import datetime as dt
import io
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import traceback
from unittest.mock import patch

import config
from scenarios import SCENARIOS, validate


def agent_trial(query, wardrobe):
    import agent
    import generate
    import trace
    evidence = {"query": query, "calls": [], "outfit_inputs": [], "caption_inputs": []}
    original_search = agent.call_tool
    original_outfit = agent.suggest_outfit
    original_caption = agent.create_fit_card
    def search(name, arguments):
        evidence['calls'].append(name + ' (MCP)')
        result = original_search(name, arguments)
        if name == 'search_listings':
            evidence['search_return'] = copy.deepcopy(result)
        elif name == 'compare_prices':
            evidence['comparison_return'] = copy.deepcopy(result)
        return result
    def outfit(item, wardrobe):
        evidence['calls'].append('suggest_outfit')
        evidence['outfit_inputs'].append(copy.deepcopy({'new_item': item, 'wardrobe': wardrobe}))
        return original_outfit(item, wardrobe)
    def caption(outfit, item):
        evidence['calls'].append('create_fit_card')
        evidence['caption_inputs'].append(copy.deepcopy({'outfit': outfit, 'new_item': item}))
        return original_caption(outfit, item)
    stream = io.StringIO()
    start = generate.call_count()
    with contextlib.redirect_stdout(stream):
        try:
            with patch.object(agent, 'call_tool', side_effect=search), patch.object(agent, 'suggest_outfit', side_effect=outfit), patch.object(agent, 'create_fit_card', side_effect=caption):
                evidence['session'] = agent.run_agent(query, wardrobe)
        except Exception:
            evidence['crashed'] = traceback.format_exc()
    evidence['trace'] = trace.get_trace()
    evidence['stdout'] = stream.getvalue()
    evidence['model_calls'] = generate.call_count() - start
    return evidence


def caption_trial(attempt):
    import tools
    from utils.data_loader import load_listings
    # Fixed five different items, same ordering in before/after runs.
    item = load_listings()[attempt - 1]
    outfit = 'Style this item with neutral colors and simple accessories.'
    return {'source': 'tools.py::create_fit_card', 'new_item': item,
            'outfit': outfit, 'fit_card': tools.create_fit_card(outfit, item)}


def persistence_trial(attempt, query):
    from utils.data_loader import get_example_wardrobe
    from utils import data_loader
    item = {'id': f'eval_added_{attempt}', 'name': f'Evaluation scarf {attempt}',
            'category': 'accessories', 'colors': ['blue'], 'style_tags': ['casual']}
    wardrobe = get_example_wardrobe()
    wardrobe['items'].append(item)
    # Both child processes use the real save/load functions, with only the
    # storage directory redirected to protect the user's saved wardrobe.
    with tempfile.TemporaryDirectory(prefix='fitfindr-eval-') as directory:
        folder = Path(directory)
        # _DATA_DIR also controls listing/schema reads, so preserve those fixtures.
        for filename in ('listings.json', 'wardrobe_schema.json'):
            shutil.copy2(Path(data_loader._DATA_DIR) / filename, folder / filename)
        (folder / 'input.json').write_text(json.dumps(wardrobe))
        env = dict(os.environ, AI201_CACHE='0')
        for mode in ['save', 'load']:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                '--worker', mode, '--folder', directory, '--query', query],
                cwd=config.ROOT, env=env, capture_output=True, text=True, timeout=600)
            if result.returncode:
                raise RuntimeError(f'{mode} worker failed: {result.stderr}\n{result.stdout}')
        evidence = json.loads((folder / 'record.json').read_text())
        evidence['expected_added_item'] = item
        evidence['saved_wardrobe'] = json.loads((folder / 'my_wardrobe.json').read_text())
        evidence['save_process'] = json.loads((folder / 'save_process.json').read_text())
        return evidence


def worker(args):
    from utils import data_loader
    folder = Path(args.folder)
    data_loader._DATA_DIR = str(folder)
    if args.worker == 'save':
        data_loader.save_wardrobe(json.loads((folder / 'input.json').read_text()))
        (folder / 'save_process.json').write_text(json.dumps({'pid': os.getpid(), 'operation': 'save_wardrobe'}))
    else:
        wardrobe = data_loader.load_saved_wardrobe()
        evidence = agent_trial(args.query, wardrobe)
        evidence['loaded_wardrobe'] = wardrobe
        evidence['load_process_pid'] = os.getpid()
        (folder / 'record.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2))


def write_report(folder, rows, label):
    lines = [f'# Evaluation — {label}', '',
        'Five tries per criterion; caching disabled. Decide PASS/FAIL from the evidence.',
        'Sources: run_eval.py::agent_trial, agent.py::run_agent, tools.py::create_fit_card,',
        'utils/data_loader.py::save_wardrobe and load_saved_wardrobe.', '',
        '| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |',
        '|---|---|---|---|---|---|---|---|']
    for scenario, records in rows:
        lines.append(f"| {scenario['criterion']}. {scenario['name']} | {scenario['target']} | | | | | | |")
    lines += ['', '## How to judge the evidence', '',
        '1. Search, outfit and caption calls completed, with a fit card returned.',
        '2. Empty search, no suggest_outfit call, and a message naming what to change.',
        '3. Compare every field of search_return[0], session.selected_item and outfit_inputs[0].new_item.',
        '4. Each caption: 2–4 sentences, exact title once, correct price once and platform once. Check all conditions; a decimal point in a price is not a sentence ending.',
        '5. Compare expected_added_item with the saved, loaded and outfit-input wardrobe item. Save and load were separate processes. Each trial uses a different ID.',
        '', 'Do not score a crash or missing required evidence as a pass.', '']
    for scenario, records in rows:
        for i, record in enumerate(records,1):
            lines += [f"## Criterion {scenario['criterion']} — Try {i}", '',
                      '```json', json.dumps(record,ensure_ascii=False,indent=2), '```', '']
    (folder / 'report.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', default='before')
    parser.add_argument('--worker', choices=['save','load'], help=argparse.SUPPRESS)
    parser.add_argument('--folder', help=argparse.SUPPRESS)
    parser.add_argument('--query', help=argparse.SUPPRESS)
    args = parser.parse_args()
    config.CACHE_ENABLED = False
    os.environ['AI201_CACHE'] = '0'
    if args.worker:
        worker(args)
        return
    if validate():
        raise ValueError(validate())
    from utils.data_loader import get_example_wardrobe, load_listings
    assert len(load_listings()) >= 5, 'Five distinct listings required.'
    stamp = dt.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    label = ''.join(c for c in args.label if c.isalnum() or c in '-_') or 'run'
    folder = config.RESULTS_DIR / f'eval_{stamp}_{label}'
    folder.mkdir(parents=True, exist_ok=False)
    rows = []
    print(f'Cache OFF. Evidence saved after every trial in {folder}', flush=True)
    for scenario in SCENARIOS:
        records = []
        rows.append((scenario, records))
        for attempt in range(1,6):
            print(f"Criterion {scenario['criterion']}, try {attempt}/5", flush=True)
            try:
                kind = scenario['kind']
                if kind == 'caption': record = caption_trial(attempt)
                elif kind == 'persistence': record = persistence_trial(attempt, scenario['query'])
                else: record = agent_trial(scenario['query'], get_example_wardrobe())
            except Exception:
                record = {'crashed': traceback.format_exc()}
            records.append(record)
            (folder / f"criterion_{scenario['criterion']}_try_{attempt}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2))
            write_report(folder, rows, args.label)
    print(f'Finished. Review {folder / "report.md"}. No verdicts were assigned automatically.')


if __name__ == '__main__':
    main()
