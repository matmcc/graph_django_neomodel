"use strict";
/*jshint esversion: 8 */

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
    for ( i = 0 ; i < l; i++ ) {
      let el = nodes[i];
      // Bootstrap compatibility
      el.className = el.className.replace(cssClass, '');
    }
  },

  addClass: function (selectors, cssClass) {
    let nodes = document.querySelectorAll(selectors);
    let l = nodes.length;
    for ( i = 0 ; i < l; i++ ) {
      let el = nodes[i];
      // Bootstrap compatibility
      if (-1 == el.className.indexOf(cssClass)) {
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
    for ( i = 0 ; i < l; i++ ) {
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
let API_endpoint = 'http://localhost:8000/graph/sigma/paper/related/';
let filter;
let g = { nodes: [], edges: [] };
g.nodes.push(node_test);
let previous_details = [];

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
      by: 'rank',
      bins: 5,
      min: 3,
      max: 13,
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


// Add methods to sigma:
//   Add a method to the graph model that updates the graph
//   ignoring node already present (cf. throw Error):
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

// init design plugin:
let design = sigma.plugins.design(s, {
  styles: Styles,
  palette: Palette
});

// init ActiveState plugin:
let activeState = sigma.plugins.activeState(s);

let activeStateNodeEdges = function (node) {
  // update activeState
    activeState.dropNodes();
    activeState.dropEdges();
    activeState.addNodes(node.id);
    activeState.addEdges(s.graph.adjacentEdges(node.id).map(i => i.id));
};

// init locate plugin:
let locate_settings = {
  animation: {
    node: {
      duration: 800
    },
    edge: {
      duration: 300
    },
    center: {
      duration: 800
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

function locateNode (nid) {
  if (nid == '') {
    locate.center(1);
  }
  else {
    locate.nodes(nid);
  }
}

function neighbours (node) {
  return s.graph.adjacentNodes(node.id);
}


/**
 * DB functions
  */
function getData(data) {
  return new Promise( function (resolve, reject) {
    try {
      resolve(fetchJs(data));
    } catch (error) {
      reject(error);
    }
  });
}

async function fetchJs(node_id) {
  const URL = API_endpoint + node_id;
  const response = await fetch(URL);
  const result = await response.json();
  return await result;
}

function updateGraph_(s, node) {
  // Calls API to return neighbouring nodes and edges, then updates graph.
  let update = {
    nodes: [],
    edges: []
  };

  // Wait until getNodes and getEdges complete
  Promise.all([
    getData(node.id).then(values => {
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
    let neighbours = s.graph.adjacentNodes(node.id);
    // pan camera to neighbourhood location
    // if() to avoid zooming straight in when no neighbours which disorients.
    if (neighbours.length > 1) {locate.nodes(neighbours.map(n => n.id));}
        // add halo to new nodes
    s.renderers[0].halo({nodes: update.nodes, edges: []});

  });
}


/**
 * Filter pane
  */
function updatePane (graph, filter) {
  // get max degree
  let maxDegree = 0,
      minYear = 3000,
      maxYear = 0,
      maxCit = 0,
      maxRef = 0;

  // read nodes
  graph.nodes().forEach(function(n) {
    maxDegree = Math.max(maxDegree, graph.degree(n.id));
    if (typeof n.year !== "undefined") {
      minYear = Math.min(minYear, n.year);
      maxYear = Math.max(maxYear, n.year);
    }
    if (typeof n.rc !== "undefined") {
      maxRef = Math.max(maxRef, n.rc);
    }
    if (typeof n.cc !== "undefined") {
      maxCit = Math.max(maxCit, n.cc);
    }
  });

  // min degree
  _.$('min-degree').max = maxDegree;
  _.$('max-degree-value').textContent = maxDegree;
  _.$('min-refs').max = maxRef;
  _.$('max-refs-val').textContent = maxRef;
  _.$('min-cits').max = maxCit;
  _.$('max-cits-val').textContent = maxCit;

  // min and max year
  _.$('min-year').min = minYear;
  _.$('min-year-val').textContent = minYear;
  _.$('min-year').max = maxYear;
  _.$('max-year-val').textContent = maxYear;
  if (_.$('min-year').value == 0) {
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

// Initialize the Filter API
filter = sigma.plugins.filter(s);

updatePane(s.graph, filter);

function applyMinDegreeFilter(e) {
  let v = e.target.value;
  _.$('min-degree-val').textContent = v;

  filter.undo('min-degree')
          .nodesBy(function(n, options) {
                    return this.graph.degree(n.id) >= options.minDegreeVal;
                  },
                  { minDegreeVal: +v }, 'min-degree' )
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

// Return array of unique values
// see: https://stackoverflow.com/questions/1960473
function arrayUnique(array) {
  return [...new Set(array)];
}

// Details pane

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
  // Note - not checking typeof node.citations !== 'undefined' will error, same for refs - fix in js framework?
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

// Halo
function renderHalo(nodes, edges=[]) {
  s.renderers[0].halo({
    nodes: arrayUnique(nodes.map(n => n.id)),
    edges: arrayUnique(edges.map(n => n.id))
  });
}

s.bind('hovers', function(e) {
  // console.log(e.data.captor, e.data);
  if (e.data.enter.nodes.length > 0) {
    // _.$('details-text').textContent = JSON.stringify(e.data.enter.nodes[0]);
    addDiv(e.data.enter.nodes[0]);
  }
  renderHaloAdjacent(e.data.enter.nodes);
});


let renderHaloAdjacent = function (nodes) {
  var adjacentNodes = [],
      adjacentEdges = [];

  if (!nodes.length) return;

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
};


s.renderers[0].bind('render', function(e) {
  s.renderers[0].halo();
});

// Configure the ForceLink algorithm:
var fa = sigma.layouts.configForceLink(s, {
  edgeWeightInfluence: 1,
  linLogMode: true, //  emphasize clusters (and outliers)
  // randomize: 'globally',
  // seems to crash browser if true and randomize not set to globally
  // (but should speed up large graph layout)
  // barnesHutOptimize: true,
  // barnesHutTheta: 1.2,
  // strongGravityMode: true,
  worker: true,
  autoStop: true,
  avgDistanceThreshold: 0.05,
  background: true,
  easing: 'cubicInOut'
});

fa.bind('start stop', function (event) {
  console.log(event.type);
  if (event.type === 'stop') {
    document.getElementById('toggle-layout').innerHTML = 'Start layout';
  }
});

document.getElementById('toggle-layout').addEventListener('click', function() {
  if ((s.supervisor || {}).running) {
    sigma.layouts.killForceLink();
    document.getElementById('toggle-layout').innerHTML = 'Start layout';
  } else {
    sigma.layouts.startForceLink({worker: true});
    document.getElementById('toggle-layout').innerHTML = 'Stop layout';
  }
});

// Configure the Fruchterman-Reingold algorithm:
var frListener = sigma.layouts.fruchtermanReingold.configure(s, {
  iterations: 500,
  easing: 'quadraticInOut',
  duration: 800
});

_.$('FR').addEventListener("click", function(e) {
  sigma.layouts.fruchtermanReingold.start(s);
});

/**
 * Bind events
  */
s.bind('clickNode', function(e) {
  // console.log(e.type, e.data.node.id, e.data.node.label, e.data.captor);
  if (activeState.nodes().includes(e.data.node)) {
    locate.center(locate_settings.zoomDef);
  } else {
    // TODO: this may call API for node which has previously been called - fix.
    console.log(e.data.node);
    updateGraph_(s, e.data.node);
  }
  previous_details.push(e.data.node);
  addPrevNodeButton(e.data.node);
});

s.bind('doubleClickStage', function() {
  locate.center(locate_settings.zoomDef);
});

// TODO: These are not bound together - therefore one does not update as another is used - intended?
_.$('min-degree').addEventListener("input", applyMinDegreeFilter);
_.$('min-year').addEventListener("input", applyMinYearFilter);
_.$('min-refs').addEventListener("input", applyMinRefsFilter);
_.$('min-cits').addEventListener("input", applyMinCitsFilter);
_.$('hide_edges').addEventListener("change", applyHideEdgesFilter);

// s.bind('clickEdge doubleClickEdge rightClickEdge', function(e) {
//   console.log(e.type, e.data.edge, e.data.captor);
// });
// s.bind('clickStage doubleClickStage rightClickStage', function(e) {
//   console.log(e.type, e.data.captor);
// });
// s.bind('hovers', function(e) {
//   console.log(e.type, e.data.captor, e.data);
// });
