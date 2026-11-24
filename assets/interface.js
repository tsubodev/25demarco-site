import { guilhermeMoments } from './guilherme-moments.js';
import { tiagoMoments } from './tiago-moments.js';
import { installWheelInput } from './wheel-input.js';
import { routePages } from './route-pages.js';
import { introduction, peopleContent } from './people.js';
import { pointClouds as routes } from './point-clouds.js?v=fusion-1-6720-6723-exploracao';

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
let selectedPerson = '1';
let hasEntered = false;
let menuExpanded = false;
const clouds = new Map();
const currentPages = new Map();
const previousPage = document.querySelector('#page-previous');
const nextPage = document.querySelector('#page-next');

let selectedDataset;

function showSubpage(index, writeHistory = true) {
  const count = routes[selectedPerson].length;
  index = Math.max(0, Math.min(count - 1, index));
  currentPages.set(selectedPerson, index);
  const dataset = routes[selectedPerson][index];
  const mapPage = routePages[selectedPerson][index];
  selectedDataset = dataset?.code;
  const {name} = peopleContent[selectedPerson];
  const map = document.querySelector('#route-map');
  map.hidden = !mapPage;
  if (mapPage) {
    map.src = mapPage.map;
    map.alt = `Mapa do percurso de ${name}, página ${index + 1} de ${count}`;
  }
  const label = dataset ? ` · ${dataset.code}` : '';
  document.querySelector('#page-indicator').textContent = `${name}${label} · ${index + 1} / ${count}`;
  previousPage.disabled = index === 0;
  nextPage.disabled = index === count - 1;
  setupMomentViews();
  renderRoute();
  if (dataset?.sources?.length) {
    const record = clouds.get(selectedDataset);
    if (record?.ready) frameSelectedClouds(record);
    else loadViewer(dataset);
  }
  const hash = `#puxador-${selectedPerson}/pagina-${index + 1}`;
  if (writeHistory && location.hash !== hash) history.pushState(null, '', hash);
}

previousPage.addEventListener('click', () => showSubpage(currentPages.get(selectedPerson) - 1));
nextPage.addEventListener('click', () => showSubpage(currentPages.get(selectedPerson) + 1));

function visibleClouds(record) {
  return record.pointclouds.filter(cloud => cloud.visible);
}

function selectedMoments() {
  if (selectedPerson === '1' && selectedDataset === 'GPBK6717') return guilhermeMoments;
  if (selectedPerson === '3' && selectedDataset === 'GPBK6719') return tiagoMoments;
  return null;
}

const momentsPanel = document.querySelector('#tiago-moments');
const momentViews = document.querySelector('#moment-views');
const momentDescription = document.querySelector('#moment-description');
function setupMomentViews() {
  momentViews.querySelectorAll('[data-moment]:not([data-moment="overview"])').forEach(button => button.remove());
  for (const [index, moment] of (selectedMoments() ?? []).entries()) {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.moment = index;
    button.textContent = `${index + 1}. ${moment.title}`;
    momentViews.append(button);
  }
  updateMomentSelection('overview');
}

function updateMomentSelection(selection) {
  for (const button of momentViews.querySelectorAll('button')) {
    button.setAttribute('aria-pressed', String(button.dataset.moment === selection));
  }
  const moment = selectedMoments()?.[selection];
  momentDescription.hidden = !moment;
  if (moment) {
    document.querySelector('#moment-title').textContent = moment.title;
    document.querySelector('#moment-caption').textContent = moment.caption;
  }
}

function frameMomentsOverview(pointclouds) {
  viewer.controls.stop();
  viewer.controls.stopTweens?.();
  const view = viewer.scene.view;
  // Use Potree's initial orientation and fit the current canvas after hiding the caption.
  view.yaw = Math.PI / 4;
  view.pitch = -Math.PI / 4;
  const sphere = viewer.getBoundingBox(pointclouds).getBoundingSphere(new three.Sphere());
  const aspect = viewerFrame.clientWidth / Math.max(1, viewerFrame.clientHeight);
  const verticalHalfFov = viewer.scene.cameraP.fov * Math.PI / 360;
  const horizontalHalfFov = Math.atan(Math.tan(verticalHalfFov) * aspect);
  const distance = sphere.radius / Math.sin(Math.min(verticalHalfFov, horizontalHalfFov));
  view.position.copy(sphere.center).addScaledVector(view.direction, -distance);
  view.lookAt(sphere.center);
}

momentViews.addEventListener('click', event => {
  const button = event.target.closest('[data-moment]');
  const record = clouds.get(selectedDataset);
  const moments = selectedMoments();
  if (!button || !moments || !record?.ready) return;
  const selection = button.dataset.moment;
  updateMomentSelection(selection);
  if (selection === 'overview') {
    frameMomentsOverview(visibleClouds(record));
    return;
  }
  const {position, target} = moments[selection];
  viewer.controls.stop();
  viewer.controls.stopTweens?.();
  viewer.scene.view.position.set(...position);
  viewer.scene.view.lookAt(...target);
});

function syncCloudVisibility() {
  for (const [code, entry] of clouds) {
    for (const cloud of entry.pointclouds || []) {
      cloud.visible = code === selectedDataset && entry.ready;
    }
  }
}

function renderRoute() {
  const dataset = routes[selectedPerson][currentPages.get(selectedPerson)];
  const available = Boolean(dataset?.sources?.length);
  const record = clouds.get(selectedDataset);
  const loaded = available && Boolean(record?.ready);
  momentsPanel.hidden = !selectedMoments() || !loaded;
  viewerFrame.classList.toggle('route-pending', !available);
  syncCloudVisibility();
  interactionButton.hidden = !loaded;
  status.hidden = loaded;
  status.textContent = !available
    ? dataset ? `Nuvem ${dataset.code} aguardando importação.` : 'Esta etapa ainda não tem uma nuvem associada.'
    : record?.error
      ? `Não foi possível carregar a nuvem ${dataset.code}. Volte a esta etapa para tentar novamente.`
      : 'Carregando o percurso…';
}

function displayTransformFor(route) {
  // World axes: retain Y then X, and apply the final Y adjustment about the same origin.
  return new three.Matrix4().makeRotationY((route.worldYAdjustmentDegrees || 0) * Math.PI / 180)
    .multiply(new three.Matrix4().makeRotationX((route.rotationXDegrees || 0) * Math.PI / 180))
    .multiply(new three.Matrix4().makeRotationY((route.rotationYDegrees || 0) * Math.PI / 180));
}

function frameCloud(pointclouds) {
  // Frame just this route, rather than the bounding boxes of cached hidden clouds.
  const frame = new three.Object3D();
  frame.boundingBox = viewer.getBoundingBox(pointclouds);
  viewer.zoomTo(frame, 1);
  viewer.controls.stop();
}

function frameSelectedClouds(record) {
  const pointclouds = visibleClouds(record);
  if (selectedMoments()) frameMomentsOverview(pointclouds);
  else if (pointclouds.length) frameCloud(pointclouds);
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
  setMenu(false);
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
      installWheelInput(viewer);
    })();
  }
  return viewerReady;
}

function loadViewer(dataset) {
  const {code, sources} = dataset;
  const existing = clouds.get(code);
  if (existing && !existing.error) return existing.promise;
  const record = {};
  clouds.set(code, record);
  record.promise = (async () => {
    renderRoute();
    try {
      await ensureViewer();
      const transform = displayTransformFor(dataset);
      const pointclouds = await Promise.all(sources.map(async source => {
        const response = await fetch(source.url);
        if (!response.ok) throw new Error(`${source.url}: HTTP ${response.status}`);
        let timeout;
        const { pointcloud } = await Promise.race([
          Potree.loadPointCloud(source.url, source.name),
          new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('Tempo de carregamento excedido')), 45000); }),
        ]).finally(() => clearTimeout(timeout));
        pointcloud.name = source.name;
        pointcloud.userData.datasetCode = code;
        const material = pointcloud.material;
        material.size = 0.25;
        material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
        material.shape = Potree.PointShape.CIRCLE;
        material.activeAttributeName = 'rgba';
        // Apply one world-origin rotation to every segment; source coordinates stay intact.
        pointcloud.applyMatrix4(transform);
        pointcloud.visible = false;
        return pointcloud;
      }));
      record.pointclouds = pointclouds;
      record.ready = true;
      for (const pointcloud of pointclouds) viewer.scene.addPointCloud(pointcloud);
      renderRoute();
      // A previous download completing must not replace the current page's camera.
      if (selectedDataset === code && hasEntered) {
        frameSelectedClouds(record);
      }
    } catch (error) {
      console.error(`Não foi possível carregar a nuvem ${code}:`, error);
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
  const page = Math.min(Number(match[2]) - 1, routes[person].length - 1);
  if (hasEntered && selectedPerson === person) {
    if (currentPages.get(person) !== page) showSubpage(page, false);
    if (menuExpanded) setMenu(false);
  } else openExperience(person, page, false);
}
window.addEventListener('popstate', restoreLocation);
window.addEventListener('hashchange', restoreLocation);
restoreLocation();
