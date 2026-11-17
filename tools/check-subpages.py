"""Check PDF subpages, independent per-person state and shared 3D scenes."""
import argparse
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000/')
args = parser.parse_args()
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for width, height in ((1450, 1024), (390, 844)):
        page = browser.new_page(viewport={'width': width, 'height': height}, is_mobile=width < 700, has_touch=width < 700)
        errors, failures = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: failures.append((r.status, r.url)) if r.status >= 400 else None)
        page.goto(args.url)
        page.locator('.start-button').click()
        for person, count, clouds in (('1', 9, 1), ('2', 3, 1), ('3', 2, 12), ('4', 6, 17)):
            page.locator(f'[data-person="{person}"]').click()
            page.wait_for_function('(n)=>viewer.scene.pointclouds.filter(c=>c.visible).length===n', arg=clouds, timeout=45000)
            page.wait_for_function('viewer.scene.pointclouds.some(c=>c.visible && c.numVisiblePoints>0)', timeout=45000)
            page.wait_for_timeout(400)
            matrices = page.evaluate('viewer.scene.pointclouds.map(c=>c.matrix.toArray())')
            view = page.evaluate('viewer.scene.view.position.toArray()')
            loaded = page.evaluate('viewer.scene.pointclouds.length')
            assert page.locator('#page-previous').is_disabled()
            urls = []
            for index in range(count):
                assert page.locator('#page-indicator').inner_text().endswith(f'{index+1} / {count}')
                assert page.url.endswith(f'#puxador-{person}/pagina-{index+1}')
                page.wait_for_function('document.querySelector("#route-map").complete && document.querySelector("#route-map").naturalWidth>0')
                urls.append(page.locator('#route-map').get_attribute('src'))
                if person == '4' and index in (0, count - 1):
                    page.screenshot(path=f'/tmp/subpages-benne-{index+1}-{width}.png', full_page=True)
                if index < count - 1:
                    page.locator('#page-next').click()
            assert len(set(urls)) == count
            assert page.locator('#page-next').is_disabled()
            assert page.evaluate('viewer.scene.pointclouds.length') == loaded
            assert page.evaluate('viewer.scene.pointclouds.map(c=>c.matrix.toArray())') == matrices
            assert page.evaluate('viewer.scene.view.position.toArray()') == view
            page.locator('#page-previous').click()
            assert page.locator('#page-indicator').inner_text().endswith(f'{count-1} / {count}')
            page.go_back()
            page.wait_for_function('(s)=>document.querySelector("#page-indicator").textContent.endsWith(s)', arg=f'{count} / {count}')
            page.go_forward()
            page.wait_for_function('(s)=>document.querySelector("#page-indicator").textContent.endsWith(s)', arg=f'{count-1} / {count}')
            if person == '4':
                page.locator('#tour-options summary').click()
                page.locator('#tour-play').click()
                page.wait_for_function('document.querySelector("#tour-progress").value>.003')
                page.locator('#page-next').click()
                progress = page.locator('#tour-progress').evaluate('(e)=>e.value')
                page.wait_for_timeout(250)
                assert page.locator('#tour-progress').evaluate('(e)=>e.value') == progress
                assert page.locator('#tour-pause').is_disabled()
                page.locator('#page-previous').click()
            page.locator('.menu-button').click()
        # Reopening remembers Benne's selected subpage and keeps only 17 visible clouds.
        page.locator('[data-person="4"]').click()
        assert page.locator('#page-indicator').inner_text().endswith('5 / 6')
        assert page.evaluate('viewer.scene.pointclouds.length') == 31
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert not errors and not failures, (errors, failures)
        page.close()
        direct = browser.new_page(viewport={'width': width, 'height': height})
        direct.goto(args.url + '#puxador-4/pagina-6')
        direct.wait_for_function('window.viewer?.scene.pointclouds.filter(c=>c.visible).length===17', timeout=45000)
        assert direct.locator('#page-indicator').inner_text().endswith('6 / 6')
        assert direct.locator('#start-menu').is_hidden()
        assert direct.locator('#page-next').is_disabled()
        direct.close()
        print(f'PASS: {width}px; 20 subpages, limits, maps, browser history, saved page, direct link; no cloud reload or view changes', flush=True)
    browser.close()
