"""Check raw XML positions, rendering, playback and cloud origins in Chromium."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000/')
parser.add_argument('--full-playback', action='store_true', help='Also play the desktop tour in real time')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'assets/6735-trajectory.json').read_text())
source = root / data['source']
assert hashlib.sha256(source.read_bytes()).hexdigest() == data['sourceSha256']
cameras = ET.parse(source).findall('./chunk/cameras/camera')
assert len(data['frames']) == len(cameras) == 240
for frame, camera in zip(data['frames'], cameras):
    assert frame['id'] == int(camera.get('id'))
    assert frame['position'] == [float(camera.findtext('transform').split()[i]) for i in (3, 7, 11)]
def rotate(point):
    x, y, z = point
    c = math.sqrt(.5)
    return [c * (x + z), y, c * (z - x)]

positions = [rotate(f['position']) for f in data['frames']]
length = sum(math.dist(a, b) for a, b in zip(positions, positions[1:]))
expected = {'6735 / ' + p.parent.name.removesuffix(' - Cloud_converted'): rotate(json.loads(p.read_text())['boundingBox']['min'])
            for p in (root / 'pointclouds/6735').glob('*/metadata.json')}
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for width, height in ((1450, 1024), (390, 844)):
        page = browser.new_page(viewport={'width': width, 'height': height}, is_mobile=width < 600, has_touch=width < 600)
        errors, failures = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: failures.append((r.status, r.url)) if r.status >= 400 else None)
        page.goto(args.url)
        assert page.locator('#guided-route').is_hidden()
        page.locator('[data-person="4"]').click()
        page.wait_for_function('!document.querySelector("#tour-play").disabled', timeout=45000)
        page.wait_for_function('viewer.scene.pointclouds.some(c=>c.numVisiblePoints>0)', timeout=45000)
        actual = page.evaluate('Object.fromEntries(viewer.scene.pointclouds.map(c=>[c.name,c.position.toArray()]))')
        assert actual.keys() == expected.keys()
        assert all(math.dist(actual[k], expected[k]) < 1e-9 for k in expected)
        samples = page.evaluate('''() => { const g=viewer.scene.scene.getObjectByName('6735 camera trajectory').geometry;
          return Array.from({length:g.attributes.instanceStart.count},(_,i)=>[g.attributes.instanceStart.getX(i),g.attributes.instanceStart.getY(i),g.attributes.instanceStart.getZ(i)]); }''')
        assert len(samples) == 239
        for actual, target in zip(samples, positions):
            assert math.dist(actual, target) < .00002
        page.locator('#tour-path').uncheck()
        assert page.evaluate('!viewer.scene.scene.getObjectByName("6735 camera trajectory").visible')
        page.locator('#tour-path').check()
        page.screenshot(path=f'/tmp/6735-trajectory-overview-{width}.png', full_page=True)
        page.locator('#tour-play').click()
        page.wait_for_function('document.querySelector("#tour-progress").value > .003')
        page.locator('#tour-pause').click()
        position = page.evaluate('viewer.scene.view.position.toArray()')
        progress = page.locator('#tour-progress').evaluate('(e)=>e.value')
        page.wait_for_timeout(200)
        assert page.evaluate('viewer.scene.view.position.toArray()') == position
        assert page.locator('#tour-progress').evaluate('(e)=>e.value') == progress
        page.locator('#tour-play').click()
        page.wait_for_function('(v)=>document.querySelector("#tour-progress").value>v', arg=progress)
        if args.full_playback and width == 1450:
            page.wait_for_function('document.querySelector("#tour-progress").value === 1', timeout=150000)
            assert math.dist(page.evaluate('viewer.scene.view.position.toArray()'), positions[-1]) < 1e-10
            assert page.evaluate('viewer.scene.pointclouds.some(c=>c.visible && c.numVisiblePoints>0)')
            print('PASS: complete desktop tour played in real time to final XML position', flush=True)
            page.locator('#tour-restart').click()
            page.wait_for_function('document.querySelector("#tour-progress").value > .003')
        # Advance presentation time to check middle/end without a two-minute wait.
        page.evaluate('window.realNow = performance.now.bind(performance); window.offset=0; performance.now=()=>realNow()+offset')
        page.evaluate('(s)=>window.offset+=s*1000', length / 4)
        page.wait_for_function('document.querySelector("#tour-progress").value > .49')
        sample = page.evaluate('({distance: document.querySelector("#tour-progress").value, position: viewer.scene.view.position.toArray()})')
        remaining = sample['distance'] * length
        for a, b in zip(positions, positions[1:]):
            step = math.dist(a, b)
            if remaining <= step:
                wanted = [a[i] + (b[i] - a[i]) * remaining / step for i in range(3)]
                assert math.dist(wanted, sample['position']) < 1e-8
                break
            remaining -= step
        page.screenshot(path=f'/tmp/6735-trajectory-middle-{width}.png', full_page=True)
        page.evaluate('(s)=>window.offset+=s*1000', length / 2)
        page.wait_for_function('document.querySelector("#tour-progress").value === 1')
        page.evaluate('performance.now=window.realNow')
        assert page.locator('#tour-status').inner_text() == 'Visita concluída.'
        assert math.dist(page.evaluate('viewer.scene.view.position.toArray()'), positions[-1]) < 1e-10
        page.screenshot(path=f'/tmp/6735-trajectory-end-{width}.png', full_page=True)
        page.locator('#tour-restart').click()
        page.wait_for_function('document.querySelector("#tour-progress").value < .1')
        page.locator('#tour-exit').click()
        assert 'Exploração livre' in page.locator('#tour-status').inner_text()
        # Rejoining from a different free view must not teleport on click.
        page.evaluate('viewer.scene.view.position.x+=10')
        free_position = page.evaluate('viewer.scene.view.position.toArray()')
        page.locator('#tour-play').click()
        assert math.dist(page.evaluate('viewer.scene.view.position.toArray()'), free_position) < 2
        page.locator('.menu-button').click()
        assert page.locator('#guided-route').is_hidden()
        assert page.evaluate('!viewer.scene.scene.getObjectByName("6735 camera trajectory").visible')
        page.locator('[data-person="1"]').click()
        page.wait_for_function('viewer.scene.pointclouds.some(c=>c.name==="6716" && c.visible)', timeout=45000)
        assert page.locator('#guided-route').is_hidden()
        page.locator('.menu-button').click()
        page.locator('[data-person="4"]').click()
        page.locator('#tour-overview').click()
        assert page.locator('#tour-progress').evaluate('(e)=>e.value') == 0
        assert page.evaluate('viewer.scene.scene.children.filter(c=>c.name==="6735 camera trajectory").length') == 1
        actual = page.evaluate('Object.fromEntries(viewer.scene.pointclouds.filter(c=>c.name.startsWith("6735 / ")).map(c=>[c.name,c.position.toArray()]))')
        assert actual.keys() == expected.keys()
        assert all(math.dist(actual[k], expected[k]) < 1e-9 for k in expected)
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors and not failures, (errors, failures)
        print(f'PASS: {width}px; 240 XML centres, path, middle/end playback, pause/resume/restart/exit, menu/route isolation; shared +45 degree Y rotation on all 17 clouds and path', flush=True)
        page.close()
    browser.close()
