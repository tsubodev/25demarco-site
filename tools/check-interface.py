"""Browser smoke checks for the illustrative interface.
Run against a local static server with Playwright installed.
"""
import argparse
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000/')
parser.add_argument('--screenshots', type=Path, default=Path('/tmp/25demarco-ui-check'))
args = parser.parse_args()
args.screenshots.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path=which('chromium') or which('google-chrome'),args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 for width,height in ((1450,1024),(390,844),(375,667)):
  page=b.new_page(viewport={'width':width,'height':height},is_mobile=width<600,has_touch=width<600);errors=[];failed=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.on('response',lambda r:failed.append((r.status,r.url)) if r.status>=400 else None)
  page.goto(args.url)
  assert page.locator('#start-menu').is_visible()
  assert page.locator('#workspace').evaluate('(e)=>e.inert')
  assert page.evaluate('!window.viewer')
  assert page.locator('[data-person]').count()==4
  assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'horizontal overflow'
  page.screenshot(path=str(args.screenshots / f'start-menu-{width}.png'))
  page.locator('[data-person="1"]').click()
  page.wait_for_function('window.viewer?.scene.pointclouds[0]?.numVisiblePoints > 0',timeout=45000)
  assert not page.locator('#start-menu').is_visible()
  assert not page.locator('#workspace').evaluate('(e)=>e.inert')
  assert page.locator('.potree_menu_toggle').count()==0
  settings=page.evaluate('''() => {const c=viewer.scene.pointclouds[0],m=c.material;return {size:m.size,adaptive:m.pointSizeType===Potree.PointSizeType.ADAPTIVE,circle:m.shape===Potree.PointShape.CIRCLE,background:viewer.background,edl:viewer.getEDLEnabled(),clouds:viewer.scene.pointclouds.length}}''')
  assert settings==dict(size=.25,adaptive=True,circle=True,background='white',edl=False,clouds=1),settings
  rect=page.locator('.viewer-frame').bounding_box();canvas=page.locator('#potree_render_area canvas').first.bounding_box()
  assert abs(rect['width']-canvas['width'])<3 and abs(rect['height']-canvas['height'])<3,(rect,canvas)
  page.screenshot(path=str(args.screenshots / f'pointcloud-ui-{width}.png'),full_page=True)
  if width < 600:
   # Use a real browser touch gesture: screenshots and scrollTo cannot detect
   # overflow:hidden blocking user scrolling (the original regression).
   session=page.context.new_cdp_session(page)
   story=page.locator('.story-panel').bounding_box()
   start_y=min(story['y']+100,height-40)
   def swipe_up(y):
    session.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':width//2,'y':y}]})
    for step in range(1,7):
     session.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':width//2,'y':y-step*50}]})
     page.wait_for_timeout(60)
    session.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
   swipe_up(start_y)
   page.wait_for_function('window.scrollY > 0',timeout=3000)
   for _ in range(3):
    swipe_up(height-80)
   page.wait_for_function('document.querySelector(".photo-column").lastElementChild.getBoundingClientRect().bottom <= innerHeight + 2')
   assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
   print('PASS: touch scrolling reaches final photograph',width,flush=True)
   session.detach()
  page.locator('.menu-button').click()
  assert page.locator('#start-menu').is_visible()
  page.locator('[data-person="4"]').click()
  assert page.locator('#person-heading').inner_text().startswith('PUXADOR 4')
  assert page.evaluate('viewer.scene.pointclouds.length')==1
  page.keyboard.press('Escape');assert page.locator('#start-menu').is_visible()
  page.keyboard.press('Escape');assert not page.locator('#start-menu').is_visible()
  assert not errors and not failed,(errors,failed)
  print('PASS:',width,height,settings,flush=True)
  page.close()
 b.close()
