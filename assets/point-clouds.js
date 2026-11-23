// Ordered per puxador as in the Fusion 1 sheet. Entries without sources are pending.
const catalogUrl = new URL('./cloud-catalog.json', import.meta.url);
catalogUrl.search = new URL(import.meta.url).search;
const response = await fetch(catalogUrl, {cache: 'no-cache'});
if (!response.ok) throw new Error('Não foi possível carregar o catálogo de nuvens.');

export const pointClouds = await response.json();
