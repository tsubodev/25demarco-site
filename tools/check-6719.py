"""Check the 12 aligned 6719 segments in the PUXADOR 3 viewer."""
import argparse
import json
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
        page.locator('[data-person="3"]').click()
        page.wait_for_function('window.viewer?.scene.pointclouds.filter(c=>c.visible).length === 12',timeout=45000)
        page.wait_for_function('viewer.scene.pointclouds.reduce((n,c)=>n+c.numVisiblePoints,0)>0',timeout=45000)
        page.wait_for_timeout(1500)
        state = page.evaluate('''() => viewer.scene.pointclouds.map(c=>({name:c.name,position:c.position.toArray(),visible:c.visible,points:c.numVisiblePoints,size:c.material.size,adaptive:c.material.pointSizeType===Potree.PointSizeType.ADAPTIVE,circle:c.material.shape===Potree.PointShape.CIRCLE}))''')
        assert {c['name'] for c in state} == set(expected)
        for cloud in state:
            assert cloud['position'] == expected[cloud['name']]['boundingBox']['min'],cloud
            assert cloud['visible'] and cloud['size']==.25 and cloud['adaptive'] and cloud['circle'],cloud
        assert page.locator('#viewer-status').is_hidden()
        page.screenshot(path=f'/tmp/6719-{width}.png',full_page=True)
        for person, count, prefix in (('1',1,'6716'),('2',1,'6718'),('3',12,'6719 / '),('4',0,''),('3',12,'6719 / ')):
            page.locator('.menu-button').click()
            page.locator(f'[data-person="{person}"]').click()
            page.wait_for_function('(n)=>viewer.scene.pointclouds.filter(c=>c.visible).length===n',arg=count,timeout=45000)
            if count:
                assert page.evaluate('(prefix)=>viewer.scene.pointclouds.filter(c=>c.visible).every(c=>c.name.startsWith(prefix))',prefix)
        assert page.evaluate('viewer.scene.pointclouds.length') == 14
        assert not errors and not failures,(errors,failures)
        print(f'PASS: {width}px, 12 segments in one viewer, original origins preserved; 1/2/3/4 switching without duplicates',flush=True)
        print('Rendered segment points:', {c['name']:c['points'] for c in state},flush=True)
        page.close()
    browser.close()
