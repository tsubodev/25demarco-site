"""Prepare all original 6719 segments, preserving their world-coordinate origins."""
import json
from pathlib import Path
from prepare_point_cloud import prepare

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'pointclouds/6719'

if __name__ == '__main__':
    total = 0
    sources = sorted((BASE / 'original').glob('*/metadata.json'))
    if not sources:
        raise ValueError('No 6719 source segments found')
    for metadata in sources:
        source = metadata.parent
        target = BASE / 'static' / source.name
        print(source.name, flush=True)
        prepare(source, target)
        original = json.loads(metadata.read_text())
        converted = json.loads((target / 'cloud.js').read_text())
        # Potree's offset must still be the source bounding-box minimum.
        for key, value in zip(('lx','ly','lz'), original['boundingBox']['min']):
            assert converted['boundingBox'][key] == value
        total += original['points']
    print(f'PASS: {len(sources)} segments, {total} points; all origins preserved', flush=True)
