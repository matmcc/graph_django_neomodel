"use strict";
/*jshint esversion: 8 */

//region Utilities
//----------------------------------------------------------------------------------------------------------------------
/**
 * DOM utility function
 */
let _ = {
  $: function (id) {
    return document.getElementById(id);
  },

  all: function (selectors) {
    return document.querySelectorAll(selectors);
  },

  removeClass: function(selectors, cssClass) {
    let nodes = document.querySelectorAll(selectors);
    let l = nodes.length;
    for ( let i = 0 ; i < l; i++ ) {
      let el = nodes[i];
      // Bootstrap compatibility
      el.className = el.className.replace(cssClass, '');
    }
  },

  addClass: function (selectors, cssClass) {
    let nodes = document.querySelectorAll(selectors);
    let l = nodes.length;
    for ( let i = 0 ; i < l; i++ ) {
      let el = nodes[i];
      // Bootstrap compatibility
      if (-1 === el.className.indexOf(cssClass)) {
        el.className += ' ' + cssClass;
      }
    }
  },

  show: function (selectors) {
    this.removeClass(selectors, 'hidden');
  },

  hide: function (selectors) {
    this.addClass(selectors, 'hidden');
  },

  toggle: function (selectors, cssClass) {
    var cssClass = cssClass || "hidden";
    let nodes = document.querySelectorAll(selectors);
    let l = nodes.length;
    for ( let i = 0 ; i < l; i++ ) {
      let el = nodes[i];
      //el.style.display = (el.style.display != 'none' ? 'none' : '' );
      // Bootstrap compatibility
      if (-1 !== el.className.indexOf(cssClass)) {
        el.className = el.className.replace(cssClass, '');
      } else {
        el.className += ' ' + cssClass;
      }
    }
  }
};

// Return array of unique values
// see: https://stackoverflow.com/questions/1960473
function arrayUnique(array) {
  return [...new Set(array)];
}

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Fetch data
//----------------------------------------------------------------------------------------------------------------------
// AJAX requests using fetch and promises for async
// https://developer.mozilla.org/en/docs/Web/API/Fetch_API
// https://developers.google.com/web/updates/2015/03/introduction-to-fetch

function getData(query, API_endpoint) {
  return new Promise( function (resolve, reject) {
    try {
      resolve(fetchJs(query, API_endpoint));
    } catch (error) {
      reject(error);
    }
  });
}

async function fetchJs(query, API_endpoint) {
  const URL = API_endpoint + query;
  const response = await fetch(URL);
  const result = await response.json();
  return await result;
}

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Setup and constants
//----------------------------------------------------------------------------------------------------------------------
/**
 * init data
  */
let node_test = {
  "FirstPage": "1739",
  "Doctype": "Conference",
  "rank": 17157,
  "label": "What do people ask their social networks, and why?: a survey study of status message q&a behavior",
  "Publisher": "ACM",
  "BookTitle": "CHI",
  "Date": "2010-04-10",
  "cc": 464,
  "year": 2010,
  "id": 2157025439,
  "size": 1,
  "x": 75,
  "y": 1,
  "name": "what do people ask their social networks and why a survey study of status message q a behavior",
  "LastPage": "1748",
  "rc": 30,
  "DOI": "10.1145/1753326.1753587"
};
node_test.color = '#137';

// init variables
let API_related_endpoint = 'http://localhost:8000/graph/sigma/paper/related/',
    API_search_endpoint = "http://localhost:8000/graph/interpret/",
    API_cocited_endpoint = 'http://localhost:8000/graph/sigma/paper/cocited/';
let API_endpoint = API_related_endpoint;
let filter;
let g = { nodes: [], edges: [] };
g.nodes.push(node_test);
let previous_details = [];
//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Search
//----------------------------------------------------------------------------------------------------------------------
let search = _.$("MAGsearch");  // search input in Html

search.addEventListener("keyup", function (event) {
  if(event.key === "Enter") {
    searchMAG(search.value);
    search.value = null;
  }
});

_.$("MAGsearchBtn").addEventListener("click", function () {
  if(search.value !== null || undefined){
    searchMAG(search.value);
    search.value = null;
  }
});

function searchMAG(query) {
  let search_endpoint = API_search_endpoint;
  Promise.resolve(getData("?query="+query, search_endpoint)).then(values => {
    // Update graph
    s.graph.updateSkipDuplicateNodes(values);
    }).then(()=>{
      // re-apply design
      design.deprecate();
      design.apply();
      s.refresh();
      updatePane(s.graph, filter);
  });
}

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Sigma setup, settings, Init graph
//----------------------------------------------------------------------------------------------------------------------
// see: https://github.com/jacomyal/sigma.js/wiki/
// and 'examples' - demo html files: https://github.com/jacomyal/sigma.js


// Add methods to sigma:
// https://github.com/jacomyal/sigma.js/wiki/Graph-API
// Add a method to the graph model that updates the graph
// ignoring node already present (cf. throw Error):
sigma.classes.graph.addMethod('updateSkipDuplicateNodes', function(g) {

  for (let node of g.nodes) {
    if (!(this.nodesIndex.get(node.id))) {
       this.addNode(node);}
  }

  for (let edge of g.edges) {
    if (!(this.edgesIndex.get(edge.id))) {
      this.addEdge(edge);
    }
  }

  return this;
});

//https://github.com/jacomyal/sigma.js/wiki/Settings
/**
 * Init sigma graph
  */
// sigma settings
let settings = {
  nodeActiveColor: 'default',
  nodeBorderSize: 1,
  nodeActiveBorderSize: 2,
  nodeActiveOuterBorderSize: 3,
  defaultNodeBorderColor: '#fff',
  defaultNodeHoverBorderColor: '#fff',
  defaultNodeActiveBorderColor: '#fff',
  defaultNodeActiveOuterBorderColor: 'rgb(236, 81, 72)',

  labelActiveColor: 'default',
  labelThreshold: 21,
  labelColor: 'node',
  defaultLabelSize: 12,
  // labelSize: 'proportional',
  // labelSizeRatio: 2
  maxNodeLabelLineLength: 25,

  zoomMin: 0.001,
  zoomMax: 3,
  doubleClickEnabled: false,

  nodeHaloColor: '#ffc021',
  edgeHaloColor: '#f0f061',
  nodeHaloSize: 6,
  edgeHaloSize: 2,

  // enableEdgeHovering: true,  // canvas renderer only
  // edgeHoverPrecision: 5,
  shortLabelsOnHover: true,    // enable the short label display mode
  // spriteSheetResolution: 2048, // resolution of the sprite sheet square
  // spriteSheetMaxSprites: 8     // number max of sprites

  animationsTime: 500,
};

// init sigma
let s = new sigma({
  graph: g,
  renderer: {
    container: document.getElementById('graph-container'),
    type: 'webgl' // 'canvas'
  },
  settings: settings
});

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Sigma Update Graph
//----------------------------------------------------------------------------------------------------------------------
// This function updates the graph and then updates relevant functions and plugins to match the newly loaded data.
function updateGraph_(s, node) {
  // Calls API to return neighbouring nodes and edges, then updates graph.
  let update = {
    nodes: [],
    edges: []
  };

  // Wait until getNodes and getEdges complete
  Promise.all([
    getData(node.id, API_endpoint).then(values => {
      update = values;
    })
  ]).then(values => {
    console.log(update);
    // then update graph
    s.graph.updateSkipDuplicateNodes(update);
    // re-apply design
    design.deprecate();
    design.apply();
    }).then(()=>{
      // apply activeState to node and connected edges
    activeStateNodeEdges(node);
    }).then(()=>{
    // refresh graph
    s.refresh();
    // update filters pane
    updatePane(s.graph, filter);
  }).then(() => {
    // s.startNoverlap();
    let neighbours = s.graph.adjacentNodes(node.id);
    // pan camera to neighbourhood location
    // if() to avoid zooming straight in when no neighbours which disorients.
    if (neighbours.length > 1) {locate.nodes(neighbours.map(n => n.id));}
        // add halo to new nodes
  //   s.renderers[0].halo({nodes: update.nodes, edges: []});
  //   console.log(neighbours);
  //   neighbours.forEach(function (n) {
  //   n.x_prev = n.x;
  //   n.y_prev = n.y;
  // });
  //   storeLayoutAsPrevLayout(neighbours);
  });
}

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Sigma Design plugin
//----------------------------------------------------------------------------------------------------------------------
// https://github.com/Linkurious/linkurious.js/tree/develop/plugins/sigma.plugins.design
/*
  This plugin provides an API to design the graph visualization like a boss.
  The graph design is made of a color palette and a set of styles.
  A style is a mapping between a node or edge property and a visual variable,
  with optional parameters depending on the visual variable.
*/

/**
 * Design
 */
let Palette = {
  cb: {
    YlGn: sigma.plugins.colorbrewer.YlGn,
    YlGnBu: sigma.plugins.colorbrewer.YlGnBu,
    YlOrRd: sigma.plugins.colorbrewer.YlOrRd,
    YlOrBr: sigma.plugins.colorbrewer.YlOrBr,
    RdYlBu: sigma.plugins.colorbrewer.RdYlBu,
    Greys: sigma.plugins.colorbrewer.Greys,
    Greens: sigma.plugins.colorbrewer.Greens,
    Spectral: sigma.plugins.colorbrewer.Spectral,
    Paired: sigma.plugins.colorbrewer.Paired,
  },
  sequentialBlue: {
    7: ['#132b43','#1d3f5d','#27547a','#326896','#3d7fb5','#4897d4','#54aef3']
  },
  aSetScheme: {
    7: ["#e41a1c","#377eb8","#4daf4a","#984ea3","#ff7f00","#ffff33","#a65628"]
  },
};

let Styles = {
  nodes: {
    // label: {
    //   by: 'id',
    //   format: function (value) { return '#' + value; }
    // },
    size: {
      by: 'cc',
      bins: 9,
      min: 3,
      max: 18,
    },
    color: {
      by: 'rank',
      scheme: 'sequentialBlue',
      bins: 7,
    },
    // icon: {
    //   by: 'data.quality',
    //   scheme: 'iconScheme'
    // },
  },
  edges: {
    color: {
      by: 'w',
      scheme: 'cb.Greens',
      bins: 7
    },
    // size: {
    //   by: 'source',
    //   bins: 7,
    //   min: 1,
    //   max: 5
    // },


  }
};

// init design plugin:
let design = sigma.plugins.design(s, {
  styles: Styles,
  palette: Palette
});

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Sigma ActiveState plugin
//----------------------------------------------------------------------------------------------------------------------
// https://github.com/Linkurious/linkurious.js/tree/develop/plugins/sigma.plugins.activeState
// This plugin provides a new state called active to nodes and edges.

// init ActiveState plugin:
let activeState = sigma.plugins.activeState(s);

let activeStateNodeEdges = function (node) {
  // update activeState
    activeState.dropNodes();
    activeState.dropEdges();
    activeState.addNodes(node.id);
    activeState.addEdges(s.graph.adjacentEdges(node.id).map(i => i.id));
};

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Sigma Locate plugin
//----------------------------------------------------------------------------------------------------------------------
// https://github.com/Linkurious/linkurious.js/tree/develop/plugins/sigma.plugins.locate
// Locate nodes and edges in the visualization by animating the camera to fit the specified elements on screen.

// init locate plugin:
let locate_settings = {
  animation: {
    node: {
      duration: 1200
    },
    edge: {
      duration: 800
    },
    center: {
      duration: 1200
    }
  },
  // PADDING:
  padding: {
    top: 20,
    right: 10,
    bottom: 20,
    left: 10
  },
  // GLOBAL SETTINGS:
  // focusOut: true,
  zoomDef: 1
};

let locate = sigma.plugins.locate(s, locate_settings);

function locateNode (node_id) {
  if (node_id == '') {
    locate.center(1);
  } else {
    locate.nodes(node_id);
  }
}

function neighbours (node) {
  return s.graph.adjacentNodes(node.id);
}

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Filter Pane
//----------------------------------------------------------------------------------------------------------------------
// Updates the filter pane when new items are loaded to graph
//
/**
 * Filter pane
  */
function updatePane (graph, filter) {
  // get max degree
  let maxDegree = 0,
      minYear = 3000,
      maxYear = 0,
      maxCit = 0,
      maxRef = 0,
      minRank = 50000,
      maxRank = 0;

  // read nodes
  graph.nodes().forEach(function(n) {
    maxDegree = Math.max(maxDegree, graph.degree(n.id));
    if (typeof n.year !== "undefined") {
      minYear = Math.min(minYear, n.year);
      maxYear = Math.max(maxYear, n.year);
    }
    if (typeof n.rank !== "undefined") {
      minRank = Math.min(minRank, n.rank);
      maxRank = Math.max(maxRank, n.rank);
    }
    if (typeof n.rc !== "undefined") {
      maxRef = Math.max(maxRef, n.rc);
    }
    if (typeof n.cc !== "undefined") {
      maxCit = Math.max(maxCit, n.cc);
    }
  });

  // min degree
  _.$('rank-range').min = minRank;
  _.$('min-rank-val').textContent = maxRank;
  _.$('rank-val').textContent = _.$('rank-range').value;
  _.$('max-rank-val').textContent = minRank;
  _.$('rank-range').max = maxRank;
  // _.$('max-degree-value').textContent = maxRank;
  _.$('min-refs').max = maxRef;
  _.$('max-refs-val').textContent = maxRef;
  _.$('min-cits').max = maxCit;
  _.$('max-cits-val').textContent = maxCit;

  // min and max year
  _.$('min-year').min = minYear;
  _.$('min-year-val').textContent = minYear;
  _.$('min-year').max = maxYear;
  _.$('max-year-val').textContent = maxYear;
  if (_.$('min-year').value === 0) {
    _.$('min-year').value = minYear;
  }
  _.$('year-val').textContent = _.$('min-year').value;

  // reset button
  _.$('reset-btn').addEventListener("click", function(e) {
    _.$('min-degree').value = 0;
    _.$('min-degree-val').textContent = '0';
    _.$('min-year').value = minYear;
    _.$('year-val').textContent = minYear;
    _.$('min-refs').value = 0;
    _.$('min-refs-val').textContent = '0';
    _.$('min-cits').value = 0;
    _.$('min-cits-val').textContent = '0';
    filter.undo().apply();
    _.$('dump').textContent = '';
    _.hide('#dump');
  });

  // export button
  _.$('export-btn').addEventListener("click", function(e) {
    let chain = filter.serialize();
    console.log(chain);
    _.$('dump').textContent = JSON.stringify(chain);
    _.show('#dump');
  });
}

// TODO: These are not bound together - therefore one does not update as another is used - intended?
_.$('rank-range').addEventListener("input", applyMinDegreeFilter);
_.$('min-year').addEventListener("input", applyMinYearFilter);
_.$('min-refs').addEventListener("input", applyMinRefsFilter);
_.$('min-cits').addEventListener("input", applyMinCitsFilter);
_.$('hide_edges').addEventListener("change", applyHideEdgesFilter);

let API_mode = _.$('expansion-mode');
API_mode.addEventListener("change", function () {
  API_endpoint = "http://localhost:8000/graph/sigma/paper/" + API_mode.value + "/";
  console.log(API_endpoint);
});

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Sigma Filter plugin
//----------------------------------------------------------------------------------------------------------------------
// https://github.com/Linkurious/linkurious.js/tree/develop/plugins/sigma.plugins.filter
// filter nodes and edges by predicate, chain filters, undo and redo

// Initialize the Filter API
filter = sigma.plugins.filter(s);
// link with filter control pane
updatePane(s.graph, filter);

// function applyMinDegreeFilter(e) {
//   let v = e.target.value;
//   _.$('min-degree-val').textContent = v;
//
//   filter.undo('min-degree')
//           .nodesBy(function(n, options) {
//                     return this.graph.degree(n.id) >= options.minDegreeVal;
//                   },
//                   { minDegreeVal: +v }, 'min-degree' )
//           .apply();
// }

function applyMinDegreeFilter(e) {
  let v = e.target.value;
  _.$('rank-val').textContent = v;

  filter.undo('filter-rank')
          .nodesBy(function(n, options) {
                    return n.rank <= options.rankVal;
                  },
                  { rankVal: +v }, 'filter-rank' )
          .apply();
}

function applyMinYearFilter(e) {
  let v = e.target.value;
  _.$('year-val').textContent = v;

  filter.undo('min-year')
          .nodesBy(function(n, options) {
                    return n.year >= options.minYearVal;
                  },
                  { minYearVal: +v }, 'min-year' )
          .apply();
}

function applyMinRefsFilter(e) {
  let v = e.target.value;
  _.$('refs-val').textContent = v;

  filter.undo('min-refs')
          .nodesBy(function(n, options) {
                    return n.rc >= options.minRefsVal;
                  },
                  { minRefsVal: +v }, 'min-refs' )
          .apply();
}

function applyMinCitsFilter(e) {
  let v = e.target.value;
  _.$('cits-val').textContent = v;

  filter.undo('min-cits')
          .nodesBy(function(n, options) {
                    return n.cc >= options.minCitsVal;
                  },
                  { minCitsVal: +v }, 'min-cits' )
          .apply();
}

function applyHideEdgesFilter(e) {
  if (e.target.checked) {
    filter.undo('hide-edges')
        .edgesBy(function(e) {
              return activeState.edges().includes(e);
            },
            'hide-edges' )
        .apply();
  } else {
    filter.undo('hide-edges').apply();
  }
}

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Details pane
//----------------------------------------------------------------------------------------------------------------------
// Displays node details in details pane, add's buttons (crumbs) for clicked nodes

// Create <div> with node details
function addDiv(node) {
  let el = _.$('details');
  while (el.firstChild) {el.removeChild(el.firstChild);}

  const div = document.createElement('div');
  // div.classname = "";
  div.innerHTML = `
  <h3>${node.label}</h3>
  <p><b>Authors:</b> ${node.authors}</p>
  <p>
  <b>Year:</b> ${node.year}, 
  <b>Reference count:</b> ${typeof node.rc !== "undefined" ? node.rc : 0}, 
  <b>Citation count:</b> ${typeof node.cc !== "undefined" ? node.cc : 0},
  <b>MAG Rank:</b> ${node.rank} - 
  <a href="${node.source}" target="_blank">Source</a> - 
  <a href="https://doi.org/${node.doi}" target="_blank">DOI</a>
  </p>
  <p><b>Abstract:</b> ${node.abstract}</p>
  `;
  _.$('details').appendChild(div);
}

function addPrevNodeButton(node) {
  let el = _.$('details-header');
  const button = document.createElement('input');
  button.type = "button";
  button.id = "btn_" + node.id;
  button.value = previous_details.length;
  button.name =  "btn_" + previous_details.length;
  button.onclick = function () {
    let nbrs = s.graph.adjacentNodes(node.id);
    if (nbrs.length > 1) {locate.nodes(nbrs.map(n => n.id));}
    // renderHaloAdjacent([node]); // cannot get to work although calling from console works
    activeStateNodeEdges(node);
    addDiv(node);
  };
  el.appendChild(button);
}

// Bind hover event to adding details div - see also halo below
s.bind('hovers', function(e) {
  if (e.data.enter.nodes.length > 0) {
    addDiv(e.data.enter.nodes[0]);
  }
  renderHaloAdjacent(e.data.enter.nodes);
});

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Sigma Halo plugin
//----------------------------------------------------------------------------------------------------------------------
// https://github.com/Linkurious/linkurious.js/tree/develop/plugins/sigma.renderers.halo
// This plugin provides a method to render a halo behind nodes and edges.
// This is bound to 'hover' event - see Details region

// Halo
function renderHalo(nodes, edges=[]) {
  s.renderers[0].halo({
    nodes: arrayUnique(nodes.map(n => n.id)),
    edges: arrayUnique(edges.map(n => n.id))
  });
}

function renderHaloAdjacent (nodes) {
  let adjacentNodes = [],
      adjacentEdges = [];

  if (!nodes.length) { return; }

// Get adjacent nodes:
  nodes.forEach(function(node) {
    adjacentNodes = adjacentNodes.concat(s.graph.adjacentNodes(node.id));
  });
// Add hovered nodes to the array and remove duplicates:
  adjacentNodes = arrayUnique(adjacentNodes.concat(nodes));

// Get adjacent edges:
  nodes.forEach(function(node) {
    adjacentEdges = adjacentEdges.concat(s.graph.adjacentEdges(node.id));
  });
// Remove duplicates:
  adjacentEdges = arrayUnique(adjacentEdges);

// Render halo:
  s.renderers[0].halo({
    nodes: adjacentNodes,
    edges: adjacentEdges
  });
}

// bind render event to halo - halo is drawn in another layer, so must be re-rendered if e.g. graph is zoomed
s.renderers[0].bind('render', function(e) {
  s.renderers[0].halo();
});

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Layout
//----------------------------------------------------------------------------------------------------------------------
// Layout algorithms.
// Default layout from server passes x: year and y: rank
// other layouts calculated in browser.

// called for newly loaded nodes
function storeLayoutAsPrevLayout() {
  s.graph.nodes().forEach(function (n) {
    n.x_prev = n.x;
    n.y_prev = n.y;
  });
}

// todo: needs to test if nodes have a prev location
function loadPrevLayout() {
  s.graph.nodes().forEach(function (n) {

      let x = n.x,
          y = n.y;
      n.x_new = n.x_prev;
      n.x_prev = x;
      n.y_new = n.y_prev;
      n.y_prev = y;

  });
  sigma.plugins.animate(
      s,
      {
        x: "x_new",
        y: "y_new"
      },
      {
        duration: 1200,
      }
  );
  // s.refresh();
  // filter.undo().apply();
}
// todo: Causes interaction in graph to freeze until e.g. any filter applied.
// calling s.refresh() from browser, or applying a filter by e.g. clicking any filter control fixes this
//  but calling from the function above does not
//  a timing / binding issue?
_.$("previous-layout").addEventListener("click", loadPrevLayout);

//region Layout - NOverlap plugin
//----------------------------------------------------------------------------------------------------------------------
// https://github.com/jacomyal/sigma.js/tree/master/plugins/sigma.layout.noverlap
// Distribute nodes, ensuring they do not overlap

// Configure the noverlap layout:
var noverlapListener = s.configNoverlap({
  maxIterations: 300,
  speed: 2,
  nodeMargin: 0.5,
  scaleNodes: 1.5,  // additional margin around larger nodes
  gridSize: 100,
  easing: 'quadraticInOut', // animation transition function
  duration: 3000   // animation duration. Long here for the purposes of this example only
});
// run from graph update function

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Layout - ForceLink plugin
//----------------------------------------------------------------------------------------------------------------------
// https://github.com/Linkurious/linkurious.js/tree/develop/plugins/sigma.layouts.forceLink
// ForceAtlas2 with added functionality. See also:
// https://github.com/jacomyal/sigma.js/tree/master/plugins/sigma.layout.forceAtlas2
// Implements and extends ForceAtlas2, a force-directed layout algorithm.
// Computations are delegated to a web worker.
// Suitable for larger graphs.

// Configure the ForceLink algorithm:
var fa = sigma.layouts.configForceLink(s, {
  edgeWeightInfluence: 1,
  linLogMode: true, //  emphasize clusters (and outliers)
  randomize: 'globally',
  barnesHutOptimize: true,  // seems to crash browser if true and randomize not set to globally
  barnesHutTheta: 1.2,      // (but should speed up large graph layout)
  strongGravityMode: true,
  worker: true,
  autoStop: true,
  avgDistanceThreshold: 0.05,
  background: true,       //  Calculate positions, then update view
  easing: 'quadraticInOut',
  duration: 1500,
});

_.$('FL-layout').addEventListener('click', function() {
  if ((s.supervisor || {}).running) {
    sigma.layouts.killForceLink();
    _.$('FL-layout').innerHTML = 'Force';
  } else {
    storeLayoutAsPrevLayout();
    sigma.layouts.startForceLink({worker: true});
    _.$('FL-layout').innerHTML = 'Stop layout';
  }
});

fa.bind('start stop', function (event) {
  if (event.type === 'stop') {
    _.$('FL-layout').innerHTML = 'Force';
  }
  if (event.type === 'start') {
    _.$('FL-layout').innerHTML = 'Stop layout';
  }
});

//----------------------------------------------------------------------------------------------------------------------
//endregion

//region Layout - Fruchterman-Reingold plugin
//----------------------------------------------------------------------------------------------------------------------
// https://github.com/Linkurious/linkurious.js/tree/develop/plugins/sigma.layouts.fruchtermanReingold
// Implements the Fruchterman-Reingold layout, a force-directed layout algorithm.
// Suitable for smaller graphs
// number nodes < 1000 seems ok
// > 1000 nodes - may become impractical

// Configure the Fruchterman-Reingold algorithm:
let fr = sigma.layouts.fruchtermanReingold.configure(s, {
  iterations: 100,
  easing: 'quadraticInOut',
  duration: 1500
});

_.$('FR-layout').addEventListener("click", function(e) {
  storeLayoutAsPrevLayout();
  sigma.layouts.fruchtermanReingold.start(s);
});

fr.bind('start stop', function (event) {
  if (event.type === 'stop') {
    _.$('FR-layout').innerHTML = 'Spring';
  }
  if (event.type === 'start') {
    _.$('FR-layout').innerHTML = 'Stop layout';
  }
});

//----------------------------------------------------------------------------------------------------------------------
//endregion
//----------------------------------------------------------------------------------------------------------------------
//endregion

/**
 * Bind events
  */
s.bind('clickNode', function(e) {
  if (activeState.nodes().includes(e.data.node)) {
    locate.center(locate_settings.zoomDef);
  } else {
    console.log(e.data.node);
    updateGraph_(s, e.data.node);
  }
  previous_details.push(e.data.node);
  addPrevNodeButton(e.data.node);
});

s.bind('doubleClickStage', function() {
  locate.center(locate_settings.zoomDef);
});
