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
  const loaded = Boolean(record?.pointcloud);
  viewerFrame.classList.toggle('route-pending', !available);
  for (const [person, entry] of clouds) {
    if (entry.pointcloud) entry.pointcloud.visible = person === selectedPerson;
  }
  interactionButton.hidden = !loaded;
  status.hidden = loaded;
  status.textContent = !available
    ? 'O percurso deste puxador será adicionado em breve.'
    : record?.error
      ? 'Não foi possível carregar o percurso. Atualize a página para tentar novamente.'
      : 'Carregando o percurso…';
}

function frameCloud(pointcloud) {
  // Frame just this route, rather than the bounding boxes of cached hidden clouds.
  const frame = new three.Object3D();
  frame.boundingBox = viewer.getBoundingBox([pointcloud]);
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
  const cloud = clouds.get(person)?.pointcloud;
  if (cloud) frameCloud(cloud);
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
      const response = await fetch(route.url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      let timeout;
      const { pointcloud } = await Promise.race([
        Potree.loadPointCloud(route.url, route.name),
        new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('Tempo de carregamento excedido')), 45000); }),
      ]).finally(() => clearTimeout(timeout));
      pointcloud.name = route.name;
      const material = pointcloud.material;
      material.size = 0.25;
      material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
      material.shape = Potree.PointShape.CIRCLE;
      material.activeAttributeName = 'rgba';
      pointcloud.visible = false;
      record.pointcloud = pointcloud;
      viewer.scene.addPointCloud(pointcloud);
      renderRoute();
      // A previous download completing must not replace the current page's camera.
      if (selectedPerson === person) frameCloud(pointcloud);
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
