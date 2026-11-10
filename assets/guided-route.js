import { Line2 } from '../vendor/potree-1.8.2/libs/three.js/lines/Line2.js';
import { LineGeometry } from '../vendor/potree-1.8.2/libs/three.js/lines/LineGeometry.js';
import { LineMaterial } from '../vendor/potree-1.8.2/libs/three.js/lines/LineMaterial.js';

// Apply the same display transform as the dataset to the path and camera centres.
export class GuidedRoute {
  constructor(viewer, THREE, url, overview, displayTransform = new THREE.Matrix4()) {
    Object.assign(this, {viewer, THREE, url, overview, displayTransform, speed: 2, distance: 0, playing: false});
    this.panel = document.querySelector('#guided-route');
    this.playButton = document.querySelector('#tour-play');
    this.pauseButton = document.querySelector('#tour-pause');
    this.restartButton = document.querySelector('#tour-restart');
    this.exitButton = document.querySelector('#tour-exit');
    this.progress = document.querySelector('#tour-progress');
    this.message = document.querySelector('#tour-status');
    this.showPath = document.querySelector('#tour-path');
    this.playButton.addEventListener('click', () => this.play());
    this.pauseButton.addEventListener('click', () => this.pause());
    this.restartButton.addEventListener('click', () => { this.reset(); this.play(); });
    this.exitButton.addEventListener('click', () => {
      this.pause();
      this.message.textContent = 'Exploração livre. Continue para voltar suavemente ao percurso.';
    });
    document.querySelector('#tour-overview').addEventListener('click', () => { this.reset(); this.overview(); });
    this.showPath.addEventListener('change', () => this.sync());
    // Manual input takes over, including the existing mobile 3D gestures.
    viewer.renderer.domElement.addEventListener('pointerdown', () => this.pause());
    viewer.renderer.domElement.addEventListener('wheel', () => this.pause(), {passive: true});
    document.addEventListener('visibilitychange', () => { if (document.hidden) this.pause(); });
    viewer.addEventListener('update', () => this.update());
  }

  setActive(active) {
    this.active = active;
    this.panel.hidden = !active;
    if (!active) this.reset();
    else this.load();
    this.sync();
  }

  load() {
    if (this.loading) return;
    this.loading = (async () => {
      try {
        const response = await fetch(new URL(this.url, import.meta.url));
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (data.frames.length < 2 || data.frames.some(f => f.position.length !== 3 || !f.position.every(Number.isFinite))) {
          throw new Error('Invalid trajectory');
        }
        this.points = data.frames.map(f => new this.THREE.Vector3(...f.position).applyMatrix4(this.displayTransform));
        this.lengths = [0];
        for (let i = 1; i < this.points.length; i++) {
          this.lengths.push(this.lengths[i - 1] + this.points[i].distanceTo(this.points[i - 1]));
        }
        this.total = this.lengths[this.lengths.length - 1];
        if (!(this.total > 0)) throw new Error('Empty trajectory');
        const geometry = new LineGeometry();
        geometry.setPositions(this.points.flatMap(point => point.toArray()));
        this.path = new Line2(geometry, new LineMaterial({color: 0x982ea8, linewidth: 3, depthTest: false, depthWrite: false}));
        this.path.name = '6735 camera trajectory';
        this.path.renderOrder = 100;
        this.path.computeLineDistances();
        const marker = (position, color) => {
          const mesh = new this.THREE.Mesh(new this.THREE.SphereGeometry(.35, 12, 8), new this.THREE.MeshBasicMaterial({color, depthTest: false}));
          mesh.position.copy(position);
          mesh.renderOrder = 101;
          this.path.add(mesh);
          return mesh;
        };
        marker(this.points[0], 0x168552);
        marker(this.points[this.points.length - 1], 0xd63a34);
        this.current = marker(this.points[0], 0xe8ae00);
        this.viewer.scene.scene.add(this.path);
        this.message.textContent = 'Percurso pronto. Linha roxa; início verde e fim vermelho.';
      } catch (error) {
        this.points = null;
        this.message.textContent = 'Não foi possível carregar a visita. Atualize a página para tentar novamente.';
        console.error('6735 trajectory:', error);
      }
      this.sync();
    })();
  }

  sync() {
    if (this.path) this.path.visible = this.active && this.showPath.checked;
    this.playButton.disabled = !this.active || !this.points || this.playing;
    this.pauseButton.disabled = !this.playing;
    this.restartButton.disabled = this.exitButton.disabled = this.showPath.disabled = !this.points;
    this.progress.value = this.total ? this.distance / this.total : 0;
    this.playButton.textContent = this.distance > 0 && this.distance < this.total ? 'CONTINUAR VISITA' : 'INICIAR VISITA';
  }

  // Piecewise linear interpolation preserves corners; arc length gives constant speed.
  positionAt(distance) {
    const d = Math.max(0, Math.min(this.total, distance));
    let i = 1;
    while (i < this.lengths.length - 1 && this.lengths[i] < d) i++;
    const span = this.lengths[i] - this.lengths[i - 1];
    return this.points[i - 1].clone().lerp(this.points[i], span ? (d - this.lengths[i - 1]) / span : 0);
  }

  frameAt(distance) {
    const position = this.positionAt(distance);
    const ahead = this.positionAt(Math.min(this.total, distance + 3));
    const direction = distance < this.total - .001
      ? ahead.sub(position)
      : position.clone().sub(this.positionAt(Math.max(0, distance - 3)));
    return {position, target: position.clone().add(direction.normalize().multiplyScalar(3))};
  }

  play() {
    if (!this.active || !this.points || this.playing) return;
    if (this.distance >= this.total) this.distance = 0;
    this.viewer.controls.stop();
    this.playing = true;
    this.lastTime = performance.now();
    // Explicit eased return from free exploration; path progress waits for arrival.
    const destination = this.frameAt(this.distance);
    this.join = {elapsed: 0, position: this.viewer.scene.view.position.clone(), target: this.viewer.scene.view.getPivot().clone(), destination};
    this.message.textContent = 'Voltando suavemente ao percurso…';
    this.sync();
  }

  pause() {
    if (!this.playing) return;
    this.playing = false;
    this.join = null;
    this.message.textContent = 'Visita pausada. Você pode explorar ou continuar.';
    this.viewer.controls.stop();
    this.sync();
  }

  reset() {
    this.pause();
    this.distance = 0;
    if (this.current) this.current.position.copy(this.points[0]);
    if (this.points) this.message.textContent = 'Percurso pronto para iniciar.';
    this.sync();
  }

  update() {
    if (this.path) {
      const canvas = this.viewer.renderer.domElement;
      this.path.material.resolution.set(canvas.clientWidth, canvas.clientHeight);
    }
    if (!this.playing) return;
    const now = performance.now();
    const delta = Math.max(0, (now - this.lastTime) / 1000);
    this.lastTime = now;
    this.viewer.controls.stop();
    let frame;
    if (this.join) {
      this.join.elapsed += delta;
      const t = Math.min(1, this.join.elapsed / 1.2);
      const eased = t * t * (3 - 2 * t);
      frame = {position: this.join.position.clone().lerp(this.join.destination.position, eased), target: this.join.target.clone().lerp(this.join.destination.target, eased)};
      if (t === 1) { this.join = null; this.message.textContent = 'Visita em andamento.'; }
    } else {
      this.distance = Math.min(this.total, this.distance + delta * this.speed);
      frame = this.frameAt(this.distance);
      this.current.position.copy(frame.position);
    }
    this.viewer.scene.view.position.copy(frame.position);
    this.viewer.scene.view.lookAt(frame.target);
    this.progress.value = this.distance / this.total;
    if (this.distance === this.total) {
      this.playing = false;
      this.message.textContent = 'Visita concluída.';
      this.sync();
    }
  }
}
