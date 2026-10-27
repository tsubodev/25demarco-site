"""Rebuild the 6716 dataset without modifying its original files."""
from pathlib import Path
from prepare_point_cloud import prepare

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    prepare(ROOT / 'pointclouds/6716-cloud', ROOT / 'pointclouds/6716-static-v2')
