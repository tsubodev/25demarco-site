// Potree 1.8.2 only registers legacy mousewheel/DOMMouseScroll listeners.
// Modern Chromium emits wheel exclusively; route it through Potree's own input
// handler so hovered objects and the selected navigation mode still work.
export function installWheelInput(viewer) {
  const canvas = viewer.renderer.domElement;
  canvas.addEventListener('wheel', event => {
    if (!viewer.inputHandler.enabled || event.ctrlKey || !Number.isFinite(event.deltaY) || event.deltaY === 0) return;
    viewer.inputHandler.onMouseWheel({
      wheelDelta: -event.deltaY,
      preventDefault: () => event.preventDefault(),
    });
  }, {passive: false});

  // Firefox/older browsers may emit legacy events for the same physical wheel
  // movement. Capture blocks Potree's legacy listeners, not native page scrolling.
  const ignoreLegacy = event => event.stopImmediatePropagation();
  canvas.addEventListener('mousewheel', ignoreLegacy, {capture: true});
  canvas.addEventListener('DOMMouseScroll', ignoreLegacy, {capture: true});
}
