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
let loading;

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

async function loadViewer() {
  if (loading) return loading;
  loading = (async () => {
    status.hidden = false;
    status.textContent = 'Carregando o percurso…';
    try {
      // Import only when entering the experience; no WebGL work behind the start screen.
      await import('../vendor/potree-1.8.2/libs/three.js/build/three.module.js');
      viewer = window.viewer = new Potree.Viewer(document.querySelector('#potree_render_area'));
      viewer.setEDLEnabled(false);
      viewer.setFOV(60);
      viewer.setPointBudget(1_000_000);
      viewer.setBackground('white');
      viewer.setDescription('');

      // Validate the entry file so a missing deployment gives an actionable message.
      const response = await fetch('pointclouds/6716-static-v2/cloud.js');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      let timeout;
      const { pointcloud } = await Promise.race([
        Potree.loadPointCloud('pointclouds/6716-static-v2/cloud.js', '6716'),
        new Promise((_, reject) => { timeout = setTimeout(() => reject(new Error('Tempo de carregamento excedido')), 45000); }),
      ]).finally(() => clearTimeout(timeout));
      pointcloud.name = '6716';
      const material = pointcloud.material;
      material.size = 0.25;
      material.pointSizeType = Potree.PointSizeType.ADAPTIVE;
      material.shape = Potree.PointShape.CIRCLE;
      material.activeAttributeName = 'rgba';
      viewer.scene.addPointCloud(pointcloud);
      viewer.fitToScreen();
      status.hidden = true;
    } catch (error) {
      console.error('Não foi possível carregar o percurso:', error);
      status.textContent = 'Não foi possível carregar o percurso. Atualize a página para tentar novamente.';
    }
  })();
  return loading;
}

people.forEach(button => button.addEventListener('click', () => {
  people.forEach(person => person.removeAttribute('aria-current'));
  button.setAttribute('aria-current', 'true');
  document.querySelector('#person-heading span').textContent = `PUXADOR ${button.dataset.person}`;
  setMenu(false);
  loadViewer();
}));
menuButton.addEventListener('click', () => {
  const isOpen = !startMenu.hidden;
  if (isOpen && !viewer) {
    setMenu(false);
    loadViewer();
  } else setMenu(!isOpen);
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && viewer) setMenu(startMenu.hidden);
});
