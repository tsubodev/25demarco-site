// Each page has an independent route; a route may contain multiple aligned segments.
// Replace a reserved null entry with { url: 'pointclouds/.../cloud.js', name: '...' }
// when its dataset has been prepared for static hosting.
export const pointClouds = {
  '1': { url: 'pointclouds/6716-static-v2/cloud.js', name: '6716' },
  '2': { url: 'pointclouds/6718-static/cloud.js', name: '6718' },
  '3': {
    "name": "6719",
    "sources": [
      {
        "url": "pointclouds/6719/static/project1_converted/cloud.js",
        "name": "6719 / project1"
      },
      {
        "url": "pointclouds/6719/static/project2_converted/cloud.js",
        "name": "6719 / project2"
      },
      {
        "url": "pointclouds/6719/static/project3_converted/cloud.js",
        "name": "6719 / project3"
      },
      {
        "url": "pointclouds/6719/static/project41_converted/cloud.js",
        "name": "6719 / project41"
      },
      {
        "url": "pointclouds/6719/static/project42_converted/cloud.js",
        "name": "6719 / project42"
      },
      {
        "url": "pointclouds/6719/static/project43_converted/cloud.js",
        "name": "6719 / project43"
      },
      {
        "url": "pointclouds/6719/static/project44_converted/cloud.js",
        "name": "6719 / project44"
      },
      {
        "url": "pointclouds/6719/static/project5_converted/cloud.js",
        "name": "6719 / project5"
      },
      {
        "url": "pointclouds/6719/static/project61_converted/cloud.js",
        "name": "6719 / project61"
      },
      {
        "url": "pointclouds/6719/static/project62_converted/cloud.js",
        "name": "6719 / project62"
      },
      {
        "url": "pointclouds/6719/static/project63_converted/cloud.js",
        "name": "6719 / project63"
      },
      {
        "url": "pointclouds/6719/static/project6_converted/cloud.js",
        "name": "6719 / project6"
      }
    ]
  },
  '4': null,
};
