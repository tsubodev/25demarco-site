"""Check the Fusion 1 stage order, linked maps and clouds, and browser history."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000/')
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / 'assets/cloud-catalog.json').read_text())

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=[
        '--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
    ])
    page = browser.new_page(viewport={'width': 1450, 'height': 1024})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda response: errors.append(response.url) if response.status >= 400 else None)
    page.goto(args.url)
    page.locator('.start-button').click()
    indicator = page.locator('#page-indicator')
    next_page = page.locator('#page-next')
    previous_page = page.locator('#page-previous')

    for person, count, maps in (('1', 10, 9), ('2', 5, 3), ('3', 1, 1), ('4', 4, 4)):
        page.locator(f'[data-person="{person}"]').click()
        expect(previous_page).to_be_disabled()
        for index, dataset in enumerate(catalog[person], start=1):
            expect(indicator).to_contain_text(f'{dataset["code"]} · {index} / {count}')
            assert page.url.endswith(f'#puxador-{person}/pagina-{index}')
            map_image = page.locator('#route-map')
            if index <= maps:
                expect(map_image).to_be_visible()
                page.wait_for_function('document.querySelector("#route-map").naturalWidth > 0')
            else:
                expect(map_image).to_be_hidden()

            sources = dataset.get('sources', [])
            if sources:
                page.wait_for_function(
                    '(code)=>window.viewer?.scene.pointclouds.some(c=>c.visible && c.userData.datasetCode===code && c.numVisiblePoints>0)',
                    arg=dataset['code'], timeout=45000,
                )
                visible = page.evaluate('viewer.scene.pointclouds.filter(c=>c.visible).map(c=>c.name)')
                assert visible == [source['name'] for source in sources]
                expect(page.locator('#viewer-status')).to_be_hidden()
            else:
                expect(page.locator('#viewer-status')).to_contain_text(f'{dataset["code"]} aguardando importação')
                assert page.evaluate('!window.viewer || viewer.scene.pointclouds.every(c=>!c.visible)')
            if dataset['code'] == 'GPBK6735':
                expect(page.locator('#guided-route')).to_be_visible()
            else:
                expect(page.locator('#guided-route')).to_be_hidden()

            if index < count:
                next_page.click()

        expect(next_page).to_be_disabled()
        page.locator('.menu-button').click()

    # Re-enter at the last stage, then verify history switches both ways.
    page.locator('[data-person="4"]').click()
    expect(indicator).to_contain_text('GPBK6736 · 4 / 4')
    previous_page.click()
    expect(indicator).to_contain_text('GPBK6735 · 3 / 4')
    expect(page.locator('#guided-route')).to_be_visible()
    page.go_back()
    expect(indicator).to_contain_text('GPBK6736 · 4 / 4')
    expect(page.locator('#guided-route')).to_be_hidden()
    page.go_forward()
    expect(indicator).to_contain_text('GPBK6735 · 3 / 4')
    assert page.evaluate('viewer.scene.pointclouds.length') == 39

    direct = browser.new_page(viewport={'width': 1450, 'height': 1024})
    direct.goto(args.url + '#puxador-1/pagina-2')
    expect(direct.locator('#page-indicator')).to_contain_text('GPBK6718 · 2 / 10')
    direct.wait_for_function('window.viewer?.scene.pointclouds.filter(c=>c.visible).length === 7')
    assert not errors, errors
    print('PASS: 20 stages, linked clouds and maps, pending stages, guided tour, browser history and direct link')
    browser.close()
