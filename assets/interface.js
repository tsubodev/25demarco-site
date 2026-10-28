import { pointClouds as routes } from './point-clouds.js';

const menuButton = document.querySelector('.menu-button');
const startMenu = document.querySelector('#start-menu');
const workspace = document.querySelector('#workspace');
const people = [...document.querySelectorAll('[data-person]')];
const firstPerson = people[0];
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
const clouds = new Map();

function renderRoute() {
  const available = Boolean(routes[selectedPerson]);
  const record = clouds.get(selectedPerson);
  const loaded = Boolean(record?.ready);
  viewerFrame.classList.toggle('route-pending', !available);
  for (const [person, entry] of clouds) {
    for (const cloud of entry.pointclouds || []) cloud.visible = person === selectedPerson && entry.ready;
  }
  interactionButton.hidden = !loaded;
  status.hidden = loaded;
  status.textContent = !available
    ? 'O percurso deste puxador será adicionado em breve.'
    : record?.error
      ? 'Não foi possível carregar o percurso. Atualize a página para tentar novamente.'
      : 'Carregando o percurso…';
}

function frameCloud(pointclouds) {
  // Frame just this route, rather than the bounding boxes of cached hidden clouds.
  const frame = new three.Object3D();
  frame.boundingBox = viewer.getBoundingBox(pointclouds);
  viewer.zoomTo(frame, 1);
  viewer.controls.stop();
}

function openExperience(person) {
  selectedPerson = person;
  hasEntered = true;
  people.forEach(button => {
    if (button.dataset.person === person) button.setAttribute('aria-current', 'true');
    else button.removeAttribute('aria-current');
  });
  document.querySelector('#person-heading span').textContent = `PUXADOR ${person}`;
  setInteraction(false);
  renderRoute();
  setMenu(false);
  const record = clouds.get(person);
  if (record?.ready) frameCloud(record.pointclouds);
  else if (routes[person]) loadViewer(person);
}

function setMenu(open) {
  if (open) setInteraction(false);
  document.body.classList.toggle('menu-open', open);
  startMenu.hidden = !open;
  workspace.inert = open;
  menuButton.setAttribute('aria-expanded', String(open));
  if (open) (document.querySelector('[aria-current="true"]') || firstPerson).focus();
  else menuButton.focus();
  // Potree reads its container dimensions on each frame, including after a menu close.
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
      viewer.setBackground('white');
      viewer.setDescription('');
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
        // Keep Potree's original offset/position. Never translate segments to zero.
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
menuButton.addEventListener('click', () => {
  if (startMenu.hidden) setMenu(true);
  else openExperience(selectedPerson);
});
document.addEventListener('keydown', event => {
  if (event.key !== 'Escape' || !hasEntered) return;
  if (startMenu.hidden) setMenu(true);
  else openExperience(selectedPerson);
});
