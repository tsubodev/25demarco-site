"""Package only the files served by the site, keeping original datasets in Git."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def cloud_folders():
    catalog = json.loads((ROOT / 'assets/cloud-catalog.json').read_text())
    folders = set()
    for datasets in catalog.values():
        for dataset in datasets:
            for source in dataset.get('sources', []):
                path = Path(source['url'])
                if len(path.parts) < 3 or path.parts[0] != 'pointclouds' or '..' in path.parts:
                    raise ValueError(f'Invalid cloud path: {path}')
                if not (ROOT / path).is_file():
                    raise FileNotFoundError(ROOT / path)
                if not dataset.get('rawBase'):
                    folders.add(path.parent)
    return sorted(folder for folder in folders if not any(parent in folders for parent in folder.parents))


def build(target):
    target = target.resolve()
    if target == ROOT or ROOT in target.parents:
        raise ValueError('Use an output directory outside the repository')
    # Never overwrite an existing directory or delete user files.
    target.mkdir(parents=True, exist_ok=False)
    for name in ('index.html', '.nojekyll'):
        shutil.copy2(ROOT / name, target / name)
    for name in ('assets', 'vendor', *cloud_folders()):
        shutil.copytree(ROOT / name, target / name)
    size = sum(p.stat().st_size for p in target.rglob('*') if p.is_file())
    if size >= 1_000_000_000:
        raise ValueError(f'Pages package exceeds 1 GB: {size} bytes')
    print(f'Site packaged in {target}: {size:,} bytes; originals excluded')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', type=Path)
    build(parser.parse_args().target)
