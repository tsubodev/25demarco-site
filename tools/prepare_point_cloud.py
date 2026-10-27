"""Prepare a Potree 2.0 cloud for ordinary static hosting.

Keep the source untouched. Export positions and RGB to Potree 1.7 node files,
which the unmodified official viewer can load without HTTP Range support.
"""
from collections import deque
import json
from pathlib import Path
import struct



def prepare(source, target, scale=1e-7):
    source, target = Path(source), Path(target)
    metadata = json.loads((source / 'metadata.json').read_text())
    assert metadata['version'] == '2.0' and metadata['encoding'] == 'DEFAULT'
    hierarchy = (source / 'hierarchy.bin').read_bytes()
    octree = (source / 'octree.bin').read_bytes()
    attributes = metadata['attributes']
    stride = sum(a['size'] for a in attributes)
    assert attributes[0]['name'] == 'position' and attributes[0]['type'] == 'int32'
    rgb_offset = 0
    for attribute in attributes:
        if attribute['name'] == 'rgb':
            assert attribute['type'] == 'uint16'
            break
        rgb_offset += attribute['size']
    else:
        raise ValueError('Missing RGB attribute')
    nodes = {}

    def read_chunk(name, start, size):
        queue = deque([name])
        assert size % 22 == 0 and start + size <= len(hierarchy)
        for cursor in range(start, start + size, 22):
            current = queue.popleft()
            kind, mask, count, offset, length = struct.unpack_from('<BBIQQ', hierarchy, cursor)
            if kind == 2:
                read_chunk(current, offset, length)
                continue
            assert offset + length <= len(octree) and length == count * stride
            nodes[current] = (mask, count, offset)
            queue.extend(current + str(i) for i in range(8) if mask & (1 << i))
        assert not queue

    read_chunk('r', 0, metadata['hierarchy']['firstChunkSize'])
    assert sum(n[1] for n in nodes.values()) == metadata['points']
    output = target / 'data/r'
    output.mkdir(parents=True, exist_ok=True)
    queue = deque(['r'])
    hrc = bytearray()
    min_actual = [float('inf')] * 3
    max_actual = [-float('inf')] * 3
    max_error = 0.0
    while queue:
        name = queue.popleft()
        mask, count, offset = nodes[name]
        hrc.extend(struct.pack('<BI', mask, count))
        queue.extend(name + str(i) for i in range(8) if mask & (1 << i))
        lower = list(metadata['boundingBox']['min'])
        upper = list(metadata['boundingBox']['max'])
        for digit in name[1:]:
            for axis, bit in enumerate((4, 2, 1)):
                middle = (lower[axis] + upper[axis]) / 2
                if int(digit) & bit:
                    lower[axis] = middle
                else:
                    upper[axis] = middle
        data = bytearray()
        for i in range(count):
            cursor = offset + i * stride
            raw = struct.unpack_from('<iii', octree, cursor)
            position = [raw[j] * metadata['scale'][j] + metadata['offset'][j] for j in range(3)]
            quantized = [round((position[j] - lower[j]) / scale) for j in range(3)]
            assert all(0 <= q <= 0xffffffff for q in quantized), (name, position)
            for j in range(3):
                error = abs(quantized[j] * scale + lower[j] - position[j])
                max_error = max(max_error, error)
                assert error <= scale * .501
                min_actual[j] = min(min_actual[j], position[j])
                max_actual[j] = max(max_actual[j], position[j])
            rgb = struct.unpack_from('<HHH', octree, cursor + rgb_offset)
            # Match the official Potree 2.0 decoder's RGB normalization.
            color = [v // 256 if v > 255 else v for v in rgb]
            data.extend(struct.pack('<III4B', *quantized, *color, 255))
        assert len(data) == count * 16
        (output / (name + '.bin')).write_bytes(data)
    (output / 'r.hrc').write_bytes(hrc)

    def box(lo, hi):
        return dict(zip(('lx', 'ly', 'lz', 'ux', 'uy', 'uz'), lo + hi))

    descriptor = {
        'version': '1.7', 'octreeDir': 'data', 'points': metadata['points'],
        'boundingBox': box(metadata['boundingBox']['min'], metadata['boundingBox']['max']),
        'tightBoundingBox': box(min_actual, max_actual),
        'pointAttributes': ['POSITION_CARTESIAN', 'COLOR_PACKED'],
        'spacing': metadata['spacing'], 'scale': scale,
        'hierarchyStepSize': max(len(n) for n in nodes) + 1,
    }
    (target / 'cloud.js').write_text(json.dumps(descriptor, indent=2) + '\n')
    print(f'Validated {metadata["points"]} points across {len(nodes)} nodes; max position error {max_error:.9g}')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('target', type=Path)
    args = parser.parse_args()
    prepare(args.source, args.target)
