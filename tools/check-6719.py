"""Check the 12 aligned 6719 segments in the PUXADOR 1 viewer."""
import argparse
import json
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000/')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
metadata = sorted((root / 'pointclouds/6719/original').glob('*/metadata.json'))
expected = {'6719 / ' + p.parent.name.removesuffix('_converted'): json.loads(p.read_text()) for p in metadata}
assert len(expected) == 12
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for width, height in ((1450, 1024), (390, 844)):
        page = browser.new_page(viewport={'width':width,'height':height},is_mobile=width<600,has_touch=width<600)
        errors, failures = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: failures.append((r.status,r.url)) if r.status>=400 else None)
        page.goto(args.url)
        page.locator('.start-button').click()
        page.locator('[data-person="1"]').click()
        page.wait_for_function('window.viewer?.scene.pointclouds.filter(c=>c.visible).length === 3',timeout=45000)
        assert 'GPBK6717' in page.locator('#page-indicator').inner_text()
        expected_6717 = {f'6717 / {p.parent.name.removesuffix("_converted")}':
                         json.loads(p.read_text())['boundingBox']['min']
                         for p in (root / 'pointclouds/6717/original').glob('*/metadata.json')}
        assert len(expected_6717) == 3
        assert page.evaluate('Object.fromEntries(viewer.scene.pointclouds.filter(c=>c.visible).map(c=>[c.name,c.position.toArray()]))') == expected_6717
        page.wait_for_function('viewer.scene.pointclouds.filter(c=>c.visible).every(c=>c.numVisiblePoints>0)', timeout=45000)
        page.locator('#page-next').click()
        page.wait_for_function('viewer.scene.pointclouds.filter(c=>c.visible).length === 7', timeout=45000)
        expected_6718 = {}
        for path in (root / 'pointclouds/6718/original').glob('*/metadata.json'):
            x, y, z = json.loads(path.read_text())['boundingBox']['min']
            expected_6718[f'6718 / {path.parent.name.removesuffix("_converted")}'] = [x, -y, -z]
        assert len(expected_6718) == 7
        state_6718 = page.evaluate("""viewer.scene.pointclouds.filter(c=>c.visible)
          .map(c=>({name:c.name, position:c.position.toArray(), rotation:c.quaternion.toArray()}))""")
        for cloud in state_6718:
            assert math.dist(cloud['position'], expected_6718[cloud['name']]) < 1e-9
            assert math.dist(cloud['rotation'], [1,0,0,0]) < 1e-9
        page.wait_for_function('viewer.scene.pointclouds.some(c=>c.visible && c.numVisiblePoints>0)', timeout=45000)
        page.locator('#page-next').click()
        page.wait_for_function('viewer.scene.pointclouds.filter(c=>c.visible).length === 12', timeout=45000)
        page.wait_for_function('viewer.scene.pointclouds.reduce((n,c)=>n+c.numVisiblePoints,0)>0',timeout=45000)
        page.wait_for_timeout(1500)
        state = page.evaluate('''() => viewer.scene.pointclouds.filter(c=>c.name.startsWith("6719 / ")).map(c=>({name:c.name,position:c.position.toArray(),visible:c.visible,points:c.numVisiblePoints,size:c.material.size,adaptive:c.material.pointSizeType===Potree.PointSizeType.ADAPTIVE,circle:c.material.shape===Potree.PointShape.CIRCLE}))''')
        assert {c['name'] for c in state} == set(expected)
        for cloud in state:
            assert cloud['position'] == expected[cloud['name']]['boundingBox']['min'],cloud
            assert cloud['visible'] and cloud['size']==.25 and cloud['adaptive'] and cloud['circle'],cloud
        assert page.locator('#viewer-status').is_hidden()
        page.screenshot(path=f'/tmp/6719-{width}.png',full_page=True)
        page.locator('#page-next').click()
        page.wait_for_function('viewer.scene.pointclouds.filter(c=>c.visible).length === 5', timeout=45000)
        page.locator('#page-next').click()
        assert 'GPBK6721' in page.locator('#viewer-status').inner_text()
        assert page.evaluate('viewer.scene.pointclouds.every(c=>!c.visible)')
        page.locator('#page-previous').click()
        page.go_back()
        assert 'GPBK6721' in page.locator('#page-indicator').inner_text()
        page.locator('#page-previous').click()
        for person, count in (('1',3),('2',0),('3',0),('4',17),('1',3),('4',17)):
            page.locator('.menu-button').click()
            page.locator(f'[data-person="{person}"]').click()
            if person == '4' and 'GPBK6733' in page.locator('#page-indicator').inner_text():
                for _ in range(2):
                    page.locator('#page-next').click()
            if person == '1':
                while not page.locator('#page-previous').is_disabled():
                    page.locator('#page-previous').click()
            page.wait_for_function('(n)=>viewer.scene.pointclouds.filter(c=>c.visible).length===n',arg=count,timeout=45000)
            names = page.evaluate('viewer.scene.pointclouds.filter(c=>c.visible).map(c=>c.name)')
            if person == '1':
                assert names == ['6717 / 6717.11', '6717 / 6717.12', '6717 / 6717.2']
            if person == '4':
                assert all(n.startswith('6735 / ') for n in names)
        assert page.evaluate('viewer.scene.pointclouds.length') == 44
        assert not errors and not failures,(errors,failures)
        print(f'PASS: {width}px, 12 segments in one viewer, original origins preserved; 1/2/3/4 switching without duplicates',flush=True)
        print('Rendered segment points:', {c['name']:c['points'] for c in state},flush=True)
        page.close()
    browser.close()
