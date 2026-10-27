// One independent point cloud per menu page.
// Replace a reserved null entry with { url: 'pointclouds/.../cloud.js', name: '...' }
// when its dataset has been prepared for static hosting.
export const pointClouds = {
  '1': { url: 'pointclouds/6716-static-v2/cloud.js', name: '6716' },
  '2': { url: 'pointclouds/6718-static/cloud.js', name: '6718' },
  '3': null, // 6719: awaiting upload in transferable parts.
  '4': null,
};
