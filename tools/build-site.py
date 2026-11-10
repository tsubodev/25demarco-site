"""Package only the files served by the site, keeping original datasets in Git."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
CLOUDS = (
    'pointclouds/6716-static-v2',
    'pointclouds/6718-static',
    'pointclouds/6719/static',
    'pointclouds/6735/static',
)


def build(target):
    target = target.resolve()
    if target == ROOT or ROOT in target.parents:
        raise ValueError('Use an output directory outside the repository')
    # Never overwrite an existing directory or delete user files.
    target.mkdir(parents=True, exist_ok=False)
    for name in ('index.html', '.nojekyll'):
        shutil.copy2(ROOT / name, target / name)
    for name in ('assets', 'vendor', *CLOUDS):
        shutil.copytree(ROOT / name, target / name)
    size = sum(p.stat().st_size for p in target.rglob('*') if p.is_file())
    if size >= 1_000_000_000:
        raise ValueError(f'Pages package exceeds 1 GB: {size} bytes')
    print(f'Site packaged in {target}: {size:,} bytes; originals excluded')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', type=Path)
    build(parser.parse_args().target)
