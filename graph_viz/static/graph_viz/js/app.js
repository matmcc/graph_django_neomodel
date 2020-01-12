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
  "_id":"5dbee93263c611215bca250e",
  "id":2157025439,
  "label":"collaborative web search who what where when and why",
  "x":50,
  "y":50,
  "size":1,
  "author":[{"AuN":"meredith ringel morris"},{"AuN":"jaime teevan"}],
  "year":2009,
  "cit_count":65,
  "refs":[2138621811,2047221353,2156037541,2124142520,2157025439,2170741935,2122841972,2095976990,2168717408,2102958620,2135555017,2171743956,2171593626,1998084297,2167670020,1973812756,2022555286,2064522604,2169942798,1527499847,2111363262,2163475640,2005689470,2077802345,2111141603,2077305743,2026324192,2044964526,2010975745,2135880665,2071373254,2121865870,2043777533,2150347588,2097489103,2013984993,1517685083,2114861953,2155565025,2077150935,2121120672,2097559038,2119065103,1989113549,1966791154,2127194912,2133909581,2027253226,2034778682,2098995791,1967873612,2042542628,2026569904,2005137383,2139936993,2049614562,2124625829,2048505195,2141834868,2057323446,2135972296,2084495161,1554742307,2045522293,2118429556,2080215571,2068124369,2570381267,2113788004,2218550969,1975410736,1582299396,2123829050],
  "logprob":-19.321,
  "_created":"Thu, 01 Jan 1970 00:00:00 GMT",
  "_updated":"Thu, 01 Jan 1970 00:00:00 GMT",
  "_etag":"be710b53f9200a2e237ffbc6d9eed28dd84fa1e7"};
node_test.color = '#137';

// init variables
let API_endpoint = 'http://localhost:8000/graph/sigma/paper/related/';
let filter;
let g = { nodes: [], edges: [] };
g.nodes.push(node_test);


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
      by: 'prob',
      bins: 5,
      min: 3,
      max: 13,
    },
    color: {
      by: 'prob',
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
      by: 'weight',
      scheme: 'cb.YlGn',
      bins: 5
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

// init locate plugin:
let locate_settings = {
  animation: {
    node: {
      duration: 500
    },
    edge: {
      duration: 300
    },
    center: {
      duration: 300
    }
  },
  // PADDING:
  padding: {
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
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


/**
 * DB functions
  */
let buildRefOrQuery = function(node_dict) {
  // build an or query made up of a nodes refs to send to api
  let refs = [];
  for (let ref of node_dict.refs) {
    refs.push({"id":ref.toString()});
  }
  return {"$or": refs};
};

async function fetchJSON(url = '', data = {}) {
  // fetch Json response from API
  const URL = url + JSON.stringify(data);
  const response = await fetch(URL);
  const items = await response.json();
  // API returns {_items: [stuff_we_want]}
  return await items._items;
}

function getNodes(data) {
  // returns Promise with array of nodes
  return new Promise( function(resolve, reject) {
    const NODES = 'http://localhost:5000/api/nodes?where=';
    const query = buildRefOrQuery(data);

    try {
      resolve(fetchJSON(NODES, query));
    } catch (error) {
      reject(error);
    }
  });
}

function getEdges(data) {
  // returns Promise with array of edges
  return new Promise( function(resolve, reject) {
    const EDGES = 'http://localhost:5000/api/edges?where=';
    const query = {"source": parseInt(data.id)};

    try {
      resolve(fetchJSON(EDGES, query));
    } catch (error) {
      reject(error);
    }
  });
}

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

function updateGraph_(s, data) {
  // Calls API to return neighbouring nodes and edges, then updates graph.
  let update = {
    nodes: [],
    edges: []
  };

  // Wait until getNodes and getEdges complete
  Promise.all([
    getData(data.id).then(values => {
      update = values;
    })
      // getNodes(data).then(values =>
    //   {
    //     values.forEach( (n) => {
    //     if (!s.graph.nodes(n['id'])) {
    //       update.nodes.push(n);}
    //     });
    //   }),
    // getEdges(data).then(values =>
    //   {
    //     values.forEach( (e) => {
    //       if (!s.graph.edges(e['id'])) {
    //         update.edges.push(e);}
    //     });
    //   }),
  ]).then(values => {
    console.log(update);
    // then update graph
    s.graph.updateSkipDuplicateNodes(update);
    // re-apply design
    design.deprecate();
    design.apply();
    }).then(()=>{
    // update activeState
    activeState.dropNodes();
    activeState.dropEdges();
    activeState.addNodes(data.id);
    activeState.addEdges(s.graph.adjacentEdges(data.id).map(i => i.id));
      }
  ).then(()=>{
    // refresh graph
    s.refresh();
    updatePane(s.graph, filter);
  }).then(() => {
    let neighbours = s.graph.adjacentNodes(data.id);
    // console.log(neighbours.length);
    // if() to avoid zooming straight in which disorients.
    if (neighbours.length > 1) {locate.nodes(neighbours.map(n => n.id));}
  });
}


/**
 * Filter pane
  */
function updatePane (graph, filter) {
  // get max degree
  let maxDegree = 0,
      minYear = 3000,
      maxYear = 0;

  // read nodes
  graph.nodes().forEach(function(n) {
    maxDegree = Math.max(maxDegree, graph.degree(n.id));
    minYear = Math.min(minYear, n.year);
    maxYear = Math.max(maxYear, n.year);
  });

  // min degree
  _.$('min-degree').max = maxDegree;
  _.$('max-degree-value').textContent = maxDegree;

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
  while (el.firstChild) { el.removeChild(el.firstChild)}

  const div = document.createElement('div');
  // div.classname = "";
  div.innerHTML = `
  <h3>${node.label}</h3>
  <p>
  <b>Authors:</b> ${node.authors}, 
  <b>Year:</b> ${node.year}, 
  <b>Reference count:</b> ${node.references.length}, 
  <b>Citation count:</b> ${node.citations.length} - 
  <a href="${node.source}">Source</a> - 
  <a href="https://doi.org/${node.doi}">DOI</a>
  </p>
  <p><b>Abstract:</b> ${node.abstract}</p>
  `;
  // Note - not checking typeof node.citations !== 'undefined' will error, same for refs - fix in js framework?
  _.$('details').appendChild(div);
}


// Halo
s.bind('hovers', function(e) {
  // console.log(e.data.captor, e.data);
  if (e.data.enter.nodes.length > 0) {
    // _.$('details-text').textContent = JSON.stringify(e.data.enter.nodes[0]);
    addDiv(e.data.enter.nodes[0]);
  }

  var adjacentNodes = [],
      adjacentEdges = [];

  if (!e.data.enter.nodes.length) return;

  // Get adjacent nodes:
  e.data.enter.nodes.forEach(function(node) {
    adjacentNodes = adjacentNodes.concat(s.graph.adjacentNodes(node.id));
  });

  // Add hovered nodes to the array and remove duplicates:
  adjacentNodes = arrayUnique(adjacentNodes.concat(e.data.enter.nodes));

  // Get adjacent edges:
  e.data.enter.nodes.forEach(function(node) {
    adjacentEdges = adjacentEdges.concat(s.graph.adjacentEdges(node.id));
  });

  // Remove duplicates:
  adjacentEdges = arrayUnique(adjacentEdges);

  // Render halo:
  s.renderers[0].halo({
    nodes: adjacentNodes,
    edges: adjacentEdges
  });
});

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
    // console.log(e.data.node);
    updateGraph_(s, e.data.node);
  }
});

s.bind('rightClickStage', function() {
  locate.center(locate_settings.zoomDef);
});

// TODO: These are not bound together - therefore one does not update as another is used - intended?
_.$('min-degree').addEventListener("input", applyMinDegreeFilter);
_.$('min-year').addEventListener("input", applyMinYearFilter);
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
