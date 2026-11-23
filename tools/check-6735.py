"""Check the 17 aligned 6735 segments in the PUXADOR 4 viewer."""
import argparse
import json
import math
from pathlib import Path
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000/')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
metadata = sorted((root / 'pointclouds/6735').glob('*/metadata.json'))
expected = {'6735 / ' + p.parent.name.removesuffix(' - Cloud_converted'): json.loads(p.read_text()) for p in metadata}
assert len(expected) == 17
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for width, height in ((1450, 1024), (390, 844)):
        page = browser.new_page(viewport={'width':width,'height':height},is_mobile=width<600,has_touch=width<600)
        errors, failures = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: failures.append((r.status,r.url)) if r.status>=400 else None)
        page.goto(args.url)
        page.locator('.start-button').click()
        page.locator('[data-person="4"]').click()
        page.wait_for_function('window.viewer?.scene.pointclouds.filter(c=>c.visible).length === 17',timeout=45000)
        page.wait_for_function('viewer.scene.pointclouds.reduce((n,c)=>n+c.numVisiblePoints,0)>0',timeout=45000)
        page.wait_for_timeout(1500)
        state = page.evaluate('''() => viewer.scene.pointclouds.map(c=>({name:c.name,position:c.position.toArray(),quaternion:c.quaternion.toArray(),visible:c.visible,points:c.numVisiblePoints,size:c.material.size,adaptive:c.material.pointSizeType===Potree.PointSizeType.ADAPTIVE,circle:c.material.shape===Potree.PointShape.CIRCLE}))''')
        assert {c['name'] for c in state} == set(expected)
        for cloud in state:
            x,y,z = expected[cloud['name']]['boundingBox']['min']
            c = math.sqrt(.5)
            angle = math.radians(-5)
            a = c*(x+z)
            assert math.dist(cloud['position'], [math.cos(angle)*a+math.sin(angle)*y, c*(x-z), -math.sin(angle)*a+math.cos(angle)*y]) < 1e-9,cloud
            u,v = math.sin(angle/2),math.cos(angle/2)
            ca,sa = math.cos(math.pi/8),math.sin(math.pi/8)
            assert math.dist(cloud['quaternion'], [c*(v*ca+u*sa), c*(v*sa+u*ca), c*(v*sa-u*ca), c*(v*ca-u*sa)]) < 1e-9,cloud
            assert cloud['visible'] and cloud['size']==.25 and cloud['adaptive'] and cloud['circle'],cloud
        assert page.locator('#viewer-status').is_hidden()
        page.screenshot(path=f'/tmp/6735-{width}.png',full_page=True)
        for person, count in (('1',3),('2',0),('3',0),('4',17),('1',3),('4',17)):
            page.locator('.menu-button').click()
            page.locator(f'[data-person="{person}"]').click()
            page.wait_for_function('(n)=>viewer.scene.pointclouds.filter(c=>c.visible).length===n',arg=count,timeout=45000)
            names = page.evaluate('viewer.scene.pointclouds.filter(c=>c.visible).map(c=>c.name)')
            if person == '1':
                assert names == ['6717 / 6717.11', '6717 / 6717.12', '6717 / 6717.2']
            if person == '4':
                assert all(n.startswith('6735 / ') for n in names)
        assert page.evaluate('viewer.scene.pointclouds.length') == 33
        assert not errors and not failures,(errors,failures)
        print(f'PASS: {width}px, 17 segments in one viewer, shared +45Y, +90X, -5Y world rotation verified; 1/2/3/4 switching without duplicates',flush=True)
        print('Rendered segment points:', {c['name']:c['points'] for c in state},flush=True)
        page.close()
    browser.close()
