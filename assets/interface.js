import { routePages } from './route-pages.js';
import { introduction, peopleContent } from './people.js';
import { createReferenceAxes } from './reference-axes.js';
import { GuidedRoute } from './guided-route.js';
import { pointClouds as routes } from './point-clouds.js';

const menuButton = document.querySelector('.menu-button');
const startMenu = document.querySelector('#start-menu');
const workspace = document.querySelector('#workspace');
const people = [...document.querySelectorAll('[data-person]')];
const firstPerson = people[0];
const homeContent = document.querySelector('#home-content');
const peopleMenu = document.querySelector('#people-menu');
document.querySelector('#introduction').textContent = introduction;
const status = document.querySelector('#viewer-status');
const interactionButton = document.querySelector('#viewer-interaction');
const viewerFrame = document.querySelector('.viewer-frame');

function setInteraction(active) {
  viewerFrame.classList.toggle('is-interacting', active);
  interactionButton.setAttribute('aria-pressed', String(active));
  interactionButton.textContent = active ? 'VOLTAR À ROLAGEM' : 'EXPLORAR NUVEM';
}
interactionButton.addEventListener('click', () => {
  setInteraction(interactionButton.getAttribute('aria-pressed') !== 'true');
});

let viewer;
let viewerReady;
let three;
let tour;
let referenceAxes;
const axesToggle = document.querySelector('#reference-axes-toggle');
function syncReferenceAxes() {
  if (referenceAxes) referenceAxes.visible = selectedPerson === '4' && Boolean(clouds.get('4')?.ready) && startMenu.hidden && axesToggle.checked;
}
axesToggle.addEventListener('change', syncReferenceAxes);
let selectedPerson = '1';
let hasEntered = false;
let menuExpanded = false;
const clouds = new Map();
const currentPages = new Map();
const previousPage = document.querySelector('#page-previous');
const nextPage = document.querySelector('#page-next');

function showSubpage(index, writeHistory = true) {
  const pages = routePages[selectedPerson];
  index = Math.max(0, Math.min(pages.length - 1, index));
  currentPages.set(selectedPerson, index);
  const content = peopleContent[selectedPerson];
  const map = document.querySelector('#route-map');
  map.src = pages[index].map;
  map.alt = `Mapa do percurso de ${content.name}, página ${index + 1} de ${pages.length}`;
  document.querySelector('#page-indicator').textContent = `${content.name} · ${index + 1} / ${pages.length}`;
  previousPage.disabled = index === 0;
  nextPage.disabled = index === pages.length - 1;
  // Page changes do not reposition or reload any point cloud or the free view.
  tour?.pause();
  const hash = `#puxador-${selectedPerson}/pagina-${index + 1}`;
  if (writeHistory && location.hash !== hash) history.pushState(null, '', hash);
}
previousPage.addEventListener('click', () => showSubpage(currentPages.get(selectedPerson) - 1));
nextPage.addEventListener('click', () => showSubpage(currentPages.get(selectedPerson) + 1));

function renderRoute() {
  const available = Boolean(routes[selectedPerson]);
  const record = clouds.get(selectedPerson);
  const loaded = Boolean(record?.ready);
  viewerFrame.classList.toggle('route-pending', !available);
  for (const [person, entry] of clouds) {
    for (const cloud of entry.pointclouds || []) cloud.visible = person === selectedPerson && entry.ready;
  }
  tour?.setActive(selectedPerson === '4' && loaded && startMenu.hidden);
  syncReferenceAxes();
  interactionButton.hidden = !loaded;
  status.hidden = loaded;
  status.textContent = !available
    ? 'O percurso deste puxador será adicionado em breve.'
    : record?.error
      ? 'Não foi possível carregar o percurso. Atualize a página para tentar novamente.'
      : 'Carregando o percurso…';
}

function displayTransformFor(route) {
  // World axes: first the existing Y rotation, then X, about the same origin.
  return new three.Matrix4().makeRotationX((route.rotationXDegrees || 0) * Math.PI / 180)
    .multiply(new three.Matrix4().makeRotationY((route.rotationYDegrees || 0) * Math.PI / 180));
}

function frameCloud(pointclouds) {
  // Frame just this route, rather than the bounding boxes of cached hidden clouds.
  const frame = new three.Object3D();
  frame.boundingBox = viewer.getBoundingBox(pointclouds);
  viewer.zoomTo(frame, 1);
  viewer.controls.stop();
}

function openExperience(person, page = currentPages.get(person) ?? 0, writeHistory = true) {
  selectedPerson = person;
  hasEntered = true;
  people.forEach(button => {
    if (button.dataset.person === person) button.setAttribute('aria-current', 'true');
    else button.removeAttribute('aria-current');
  });
  const content = peopleContent[person];
  document.querySelector('#person-heading span').textContent = `PUXADOR ${person} - ${content.name.toUpperCase()}`;
  document.querySelector('#person-story').textContent = content.story;
  showSubpage(page, writeHistory);
  const photos = document.querySelector('.photo-column');
  photos.replaceChildren(...content.photos.map((src, index) => {
    const image = document.createElement('img');
    image.src = src;
    image.alt = `Registro ${index + 1} do percurso de ${content.name} na região da 25 de Março`;
    image.width = 1008;
    image.height = 693;
    return image;
  }));
  document.querySelector('.story-panel').scrollTop = 0;
  setInteraction(false);
  renderRoute();
  setMenu(false);
  const record = clouds.get(person);
  if (record?.ready) frameCloud(record.pointclouds);
  else if (routes[person]) loadViewer(person);
}

function setMenu(open) {
  menuExpanded = open;
  if (open) setInteraction(false);
  const welcome = !hasEntered;
  document.body.classList.toggle('home-view', welcome);
  document.body.classList.toggle('menu-open', open || welcome);
  document.body.classList.toggle('menu-expanded', open);
  startMenu.hidden = !(open || welcome);
  peopleMenu.hidden = !open;
  homeContent.hidden = !welcome;
  homeContent.inert = open;
  workspace.inert = open || welcome;
  tour?.setActive(!open && hasEntered && selectedPerson === '4' && Boolean(clouds.get('4')?.ready));
  syncReferenceAxes();
  menuButton.setAttribute('aria-expanded', String(open));
  if (open) (document.querySelector('[aria-current="true"]') || firstPerson).focus();
  else menuButton.focus();
  window.dispatchEvent(new Event('resize'));
}

async function ensureViewer() {
  if (!viewerReady) {
    viewerReady = (async () => {
      // One viewer for all pages; create it only after a configured route is selected.
      three = await import('../vendor/potree-1.8.2/libs/three.js/build/three.module.js');
      viewer = window.viewer = new Potree.Viewer(document.querySelector('#potree_render_area'));
      viewer.setEDLEnabled(false);
      viewer.setFOV(60);
      viewer.setPointBudget(1_000_000);
      viewer.setBackground(null);
      viewer.setDescription('');
      referenceAxes = createReferenceAxes(three);
      viewer.scene.scene.add(referenceAxes);
      // Keep the origin reference legible while orbiting/zooming; this is not a ruler.
      viewer.addEventListener('update', () => {
        if (!referenceAxes.visible) return;
        const camera = viewer.scene.getActiveCamera();
        const distance = viewer.scene.view.position.distanceTo(referenceAxes.position);
        const height = Math.max(1, viewer.renderer.domElement.clientHeight);
        const span = camera.isPerspectiveCamera ? 2 * distance * Math.tan(camera.fov * Math.PI / 360) : camera.top - camera.bottom;
        const size = span * 80 / height;
        referenceAxes.scale.setScalar(Math.max(.001, size / referenceAxes.userData.axisLength));
      });
      tour = new GuidedRoute(viewer, three, routes['4'].trajectory, () => frameCloud(clouds.get('4').pointclouds),
        displayTransformFor(routes['4']));
    })();
  }
  return viewerReady;
}

async function loadViewer(person) {
  if (clouds.has(person)) return clouds.get(person).promise;
  const route = routes[person];
  const record = {};
  clouds.set(person, record);
  record.promise = (async () => {
    renderRoute();
    try {
      await ensureViewer();
      const sources = route.sources || [route];
      const displayTransform = displayTransformFor(route);
      const pointclouds = await Promise.all(sources.map(async source => {
        const response = await fetch(source.url);
        if (!response.ok) throw new Error(`${source.url}: HTTP ${response.status}`);
        let timeout;
        const { pointcloud } = await Promise.race([
          Potree.loadPointCloud(source.url, source.name),
          new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('Tempo de carregamento excedido')), 45000); }),
        ]).finally(() => clearTimeout(timeout));
        pointcloud.name = source.name;
        const material = pointcloud.material;
        material.size = 0.25;
        material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
        material.shape = Potree.PointShape.CIRCLE;
        material.activeAttributeName = 'rgba';
        // Apply one world-origin rotation to every segment; source coordinates stay intact.
        pointcloud.applyMatrix4(displayTransform);
        pointcloud.visible = false;
        return pointcloud;
      }));
      record.pointclouds = pointclouds;
      record.ready = true;
      for (const pointcloud of pointclouds) viewer.scene.addPointCloud(pointcloud);
      renderRoute();
      // A previous download completing must not replace the current page's camera.
      if (selectedPerson === person) frameCloud(record.pointclouds);
    } catch (error) {
      console.error(`Não foi possível carregar o percurso ${person}:`, error);
      record.error = true;
      renderRoute();
    }
  })();
  return record.promise;
}

people.forEach(button => button.addEventListener('click', () => {
  openExperience(button.dataset.person);
}));
menuButton.addEventListener('click', () => setMenu(!menuExpanded));
document.querySelector('.start-button').addEventListener('click', () => setMenu(true));
document.querySelector('#home-button').addEventListener('click', () => {
  hasEntered = false;
  if (location.hash) history.pushState(null, '', location.pathname + location.search);
  setInteraction(false);
  setMenu(false);
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape') return;
  if (menuExpanded || hasEntered) setMenu(!menuExpanded);
});

function restoreLocation() {
  const match = location.hash.match(/^#puxador-([1-4])\/pagina-([1-9]\d*)$/);
  if (!match) {
    if (!location.hash && hasEntered) {
      hasEntered = false;
      setInteraction(false);
      setMenu(false);
    }
    return;
  }
  const person = match[1];
  const page = Math.min(Number(match[2]) - 1, routePages[person].length - 1);
  if (hasEntered && selectedPerson === person) {
    if (currentPages.get(person) !== page) showSubpage(page, false);
    if (menuExpanded) setMenu(false);
  } else openExperience(person, page, false);
}
window.addEventListener('popstate', restoreLocation);
window.addEventListener('hashchange', restoreLocation);
restoreLocation();
