// Reference only: anchored at the unchanged world origin of the 6735 dataset.
export function createReferenceAxes(THREE) {
  const axes = new THREE.Group();
  axes.name = '6735 reference axes';
  axes.visible = false;
  const length = 10;
  axes.userData.axisLength = length;
  const origin = new THREE.Vector3();
  const specifications = [
    ['X', new THREE.Vector3(1, 0, 0), '#e53935'],
    ['Y', new THREE.Vector3(0, 1, 0), '#559c16'],
    ['Z', new THREE.Vector3(0, 0, 1), '#1976ed'],
  ];
  for (const [label, direction, color] of specifications) {
    const material = new THREE.MeshBasicMaterial({color, depthTest: false, depthWrite: false});
    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(.07, .07, length - 1, 8), material);
    shaft.position.copy(direction).multiplyScalar((length - 1) / 2);
    shaft.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), direction);
    shaft.name = `axis-${label}-shaft`;
    const head = new THREE.Mesh(new THREE.ConeGeometry(.4, 1, 12), material);
    head.position.copy(direction).multiplyScalar(length - .5);
    head.quaternion.copy(shaft.quaternion);
    head.name = `axis-${label}-head`;
    axes.add(shaft, head);
    // Negative half axes are faint references, without arrowheads.
    const negative = new THREE.Line(new THREE.BufferGeometry().setFromPoints([origin, direction.clone().multiplyScalar(-length)]),
      new THREE.LineBasicMaterial({color, transparent: true, opacity: .35, depthTest: false, depthWrite: false}));
    axes.add(negative);
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 128;
    const context = canvas.getContext('2d');
    context.font = 'bold 88px sans-serif';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.lineWidth = 6;
    context.strokeStyle = '#ffffff';
    context.strokeText(label, 64, 64);
    context.fillStyle = color;
    context.fillText(label, 64, 64);
    const sprite = new THREE.Sprite(new THREE.SpriteMaterial({map: new THREE.CanvasTexture(canvas), depthTest: false, depthWrite: false}));
    sprite.name = `axis-${label}-label`;
    sprite.position.copy(direction).multiplyScalar(length + 1.5);
    sprite.scale.set(2, 2, 1);
    axes.add(sprite);
  }
  const center = new THREE.Mesh(new THREE.SphereGeometry(.22, 12, 8), new THREE.MeshBasicMaterial({color: 0x333333, depthTest: false, depthWrite: false}));
  center.name = 'world-origin';
  axes.add(center);
  axes.traverse(object => { object.renderOrder = 110; });
  return axes;
}
