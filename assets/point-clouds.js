// Ordered per puxador as in the Fusion 1 sheet. Entries without sources are pending.
const response = await fetch(new URL('./cloud-catalog.json', import.meta.url));
if (!response.ok) throw new Error('Não foi possível carregar o catálogo de nuvens.');

export const pointClouds = await response.json();
