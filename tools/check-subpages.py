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
            assert page.locator('#guided-route, #tour-play, #tour-path, #reference-axes-toggle').count() == 0
            if dataset['code'] == 'GPBK6717':
                expect(page.locator('#tiago-moments')).to_be_visible()
                expect(page.locator('#moment-description')).to_be_hidden()
                expected_titles = ('Shopping Mix', 'Entrada da galeria', 'Quiosques e lojas', 'Primeira loja')
                poses = set()
                for moment, title in enumerate(expected_titles):
                    page.locator(f'[data-moment="{moment}"]').click()
                    expect(page.locator('#moment-title')).to_have_text(title)
                    expect(page.locator('#moment-caption')).not_to_be_empty()
                    assert page.evaluate('viewer.scene.pointclouds.filter(c=>c.visible).length') == 3
                    poses.add(tuple(page.evaluate('viewer.scene.view.position.toArray()')))
                assert len(poses) == 4
                page.locator('[data-moment="overview"]').click()
                expect(page.locator('#moment-description')).to_be_hidden()
            else:
                expect(page.locator('#tiago-moments')).to_be_hidden()

            if index < count:
                next_page.click()

        expect(next_page).to_be_disabled()
        page.locator('.menu-button').click()

    # Re-enter at the last stage, then verify history switches both ways.
    page.locator('[data-person="4"]').click()
    expect(indicator).to_contain_text('GPBK6736 · 4 / 4')
    previous_page.click()
    expect(indicator).to_contain_text('GPBK6735 · 3 / 4')
    page.go_back()
    expect(indicator).to_contain_text('GPBK6736 · 4 / 4')
    page.go_forward()
    expect(indicator).to_contain_text('GPBK6735 · 3 / 4')
    expected_segments = sum(len(dataset.get('sources', [])) for datasets in catalog.values() for dataset in datasets)
    assert page.evaluate('viewer.scene.pointclouds.length') == expected_segments

    direct = browser.new_page(viewport={'width': 1450, 'height': 1024})
    direct.goto(args.url + '#puxador-1/pagina-2')
    expect(direct.locator('#page-indicator')).to_contain_text('GPBK6718 · 2 / 10')
    direct.wait_for_function('window.viewer?.scene.pointclouds.filter(c=>c.visible).length === 7')
    page.close()
    direct.close()

    # A missing descriptor for one dataset must leave other stages usable.
    isolated = browser.new_page(viewport={'width': 1450, 'height': 1024})
    affected_url = '**/pointclouds/puxador-1/6718/static/6718.1_converted/cloud.js'
    isolate_failure = lambda route: route.fulfill(status=404, body='Missing descriptor')
    isolated.route(affected_url, isolate_failure)
    isolated.goto(args.url + '#puxador-1/pagina-1')
    isolated.wait_for_function('window.viewer?.scene.pointclouds.some(c=>c.visible && c.numVisiblePoints>0)')
    assert isolated.evaluate('viewer.scene.pointclouds.every(c=>c.userData.datasetCode==="GPBK6717")')
    isolated.locator('#page-next').click()
    expect(isolated.locator('#viewer-status')).to_contain_text('Não foi possível carregar a nuvem GPBK6718')
    isolated.locator('#page-next').click()
    isolated.wait_for_function('viewer.scene.pointclouds.some(c=>c.visible && c.userData.datasetCode==="GPBK6719" && c.numVisiblePoints>0)', timeout=45000)
    isolated.unroute(affected_url, isolate_failure)
    isolated.locator('#page-previous').click()
    isolated.wait_for_function('viewer.scene.pointclouds.filter(c=>c.visible && c.userData.datasetCode==="GPBK6718").length===7')
    assert not errors, errors
    print('PASS: 20 stages, linked clouds and maps, pending stages, free navigation, browser history, direct link and isolated 404/retry')
    browser.close()
