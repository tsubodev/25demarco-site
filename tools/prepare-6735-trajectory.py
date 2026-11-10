"""Extract the aligned 6735 cameras in the existing cloud's local coordinates."""
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'pointclouds/6735/6735 cam.xml'
TARGET = ROOT / 'assets/6735-trajectory.json'


def extract():
    chunk = ET.parse(SOURCE).getroot().find('chunk')
    # This export and the existing cloud use the same local metric frame.
    # Region R describes the crop box, not a camera-to-cloud transformation.
    if chunk.find('transform') is not None or chunk.find('./components/component/transform') is not None:
        raise ValueError('Export changed: review the camera-to-cloud transformation')
    if 'Local Coordinates (m)' not in chunk.findtext('reference', ''):
        raise ValueError('Expected the verified local metric reference system')
    frames = []
    for camera in chunk.findall('./cameras/camera'):
        if camera.get('enabled') == 'false' or camera.find('transform') is None:
            continue
        matrix = list(map(float, camera.findtext('transform').split()))
        if len(matrix) != 16 or not all(map(math.isfinite, matrix)) or matrix[12:] != [0, 0, 0, 1]:
            raise ValueError('Invalid camera transform')
        frames.append({'id': int(camera.get('id')), 'label': camera.get('label'),
                       'position': [matrix[i] for i in (3, 7, 11)], 'time': None})
    frames.sort(key=lambda f: int(re.search(r'(\d+)$', f['label']).group()))
    if len(frames) != 240 or len({f['id'] for f in frames}) != 240:
        raise ValueError('Expected all 240 aligned cameras')
    steps = [math.dist(a['position'], b['position']) for a, b in zip(frames, frames[1:])]
    threshold = max(5, 5 * statistics.median(steps))
    # Do not silently connect missing frames, separate sessions or large jumps.
    if any(b['id'] != a['id'] + 1 for a, b in zip(frames, frames[1:])) or max(steps) > threshold:
        raise ValueError('Possible recording interruption: split/review the path before publishing')
    if min(steps) == 0:
        raise ValueError('Repeated camera centres: review duplicate panoramas')
    boxes = [json.loads(p.read_text())['boundingBox'] for p in (ROOT / 'pointclouds/6735').glob('*/metadata.json')]
    for frame in frames:
        if not any(all(b['min'][i] <= frame['position'][i] <= b['max'][i] for i in range(3)) for b in boxes):
            raise ValueError(f'Camera outside the existing cloud bounds: {frame["id"]}')
    return {'version': 1, 'dataset': '6735', 'units': 'metres',
            'timing': 'presentation speed; capture timestamps unavailable',
            'validation': {'maxStep': max(steps), 'gapThreshold': threshold, 'totalDistance': sum(steps)},
            'source': str(SOURCE.relative_to(ROOT)), 'sourceSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            'coordinateSystem': '6735 existing local coordinates (metres)',
            'cameraToCloud': [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1], 'frames': frames}


if __name__ == '__main__':
    data = extract()
    TARGET.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(f'PASS: {len(data["frames"])} cameras; identity mapping to existing cloud, no origin shift')
