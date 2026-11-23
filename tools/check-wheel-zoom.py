"""Check actual Chromium wheel input on every route, plus legacy-event deduplication."""
import argparse
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000/')
args = parser.parse_args()
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    page = browser.new_page(viewport={'width':1450,'height':1024})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(args.url)
    page.locator('.start-button').click()
    for person in ('1','2','3','4'):
        page.locator(f'[data-person="{person}"]').click()
        page.wait_for_function('viewer?.scene.pointclouds.some(c=>c.visible && c.numVisiblePoints>0)', timeout=45000)
        box = page.locator('#potree_render_area canvas').first.bounding_box()
        page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.6)
        page.wait_for_timeout(200)
        before = page.evaluate('viewer.scene.view.radius')
        page.mouse.wheel(0,-120)
        page.wait_for_function('(r)=>viewer.scene.view.radius<r*.99', arg=before)
        page.wait_for_timeout(700)
        near = page.evaluate('viewer.scene.view.radius')
        page.mouse.wheel(0,120)
        page.wait_for_function('(r)=>viewer.scene.view.radius>r*1.01', arg=near)
        print(f'PASS: route {person}, real Chromium wheel zooms in/out', flush=True)
        page.locator('.menu-button').click()
    # Exactly one control event even when a browser supplies both modern + legacy input.
    page.locator('[data-person="4"]').click()
    result = page.evaluate('''() => {
      viewer.controls.stop();
      let count=0;
      const listener=()=>count++;
      viewer.controls.addEventListener('mousewheel',listener);
      const canvas=viewer.renderer.domElement;
      const wheel=new WheelEvent('wheel',{deltaY:-120,bubbles:true,cancelable:true});
      canvas.dispatchEvent(wheel);
      canvas.dispatchEvent(new WheelEvent('mousewheel',{deltaY:-120,bubbles:true,cancelable:true}));
      canvas.dispatchEvent(new MouseEvent('DOMMouseScroll',{detail:-3,bubbles:true,cancelable:true}));
      const vertical=count;
      const horizontal=new WheelEvent('wheel',{deltaX:120,deltaY:0,bubbles:true,cancelable:true});
      canvas.dispatchEvent(horizontal);
      const ctrl=new WheelEvent('wheel',{deltaY:-120,ctrlKey:true,bubbles:true,cancelable:true});
      canvas.dispatchEvent(ctrl);
      viewer.inputHandler.enabled=false;
      const disabled=new WheelEvent('wheel',{deltaY:-120,bubbles:true,cancelable:true});
      canvas.dispatchEvent(disabled);
      viewer.inputHandler.enabled=true;
      viewer.controls.removeEventListener('mousewheel',listener);
      viewer.controls.stop();
      return {vertical,count,prevented:wheel.defaultPrevented,horizontal:horizontal.defaultPrevented,ctrl:ctrl.defaultPrevented,disabled:disabled.defaultPrevented};
    }''')
    assert result == dict(vertical=1,count=1,prevented=True,horizontal=False,ctrl=False,disabled=False),result
    page.locator('#tour-options summary').click()
    page.locator('#tour-play').click()
    page.wait_for_function('document.querySelector("#tour-progress").value>.003')
    box = page.locator('#potree_render_area canvas').first.bounding_box()
    page.mouse.move(box['x']+box['width']*.5,box['y']+box['height']*.6)
    page.wait_for_timeout(100)
    before = page.evaluate('viewer.scene.view.radius')
    page.mouse.wheel(0,-120)
    page.wait_for_function('document.querySelector("#tour-pause").disabled')
    page.wait_for_function('(r)=>viewer.scene.view.radius<r*.99',arg=before)
    assert not errors,errors
    print('PASS: no double zoom, page/browser scrolling preserved for unhandled input, first wheel pauses tour and zooms',flush=True)
    browser.close()
