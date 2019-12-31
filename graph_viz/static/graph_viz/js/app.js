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
    let cssClass = cssClass || "hidden";
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
  "id":"2154216473",
  "label":"collaborative web search who what where when and why",
  "x":-4.149263352155685,
  "y":-4.927542060613632,
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

// init letiables
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
    RdYlBu: sigma.plugins.colorbrewer.RdYlBu,
    Spectral: sigma.plugins.colorbrewer.Spectral,
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
      by: 'logprob',
      bins: 7,
      min: 1,
      max: 25,
    },
    color: {
      by: 'logprob',
      scheme: 'sequentialBlue',
      bins: 7,
    },
    // icon: {
    //   by: 'data.quality',
    //   scheme: 'iconScheme'
    // },
  },
  edges: {

  }
};


// Add methods to sigma:
  // Add a method to the graph model that returns an
  // object with every neighbors of a node inside:
// sigma.classes.graph.addMethod('neighbors', function(nodeId) {
//   let k,
//           neighbors = {},
//           index = this.allNeighborsIndex[nodeId] || {};
//
//   for (k in index)
//     neighbors[k] = this.nodesIndex[k];
//
//   return neighbors;
// });


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

  shortLabelsOnHover: true,    // enable the short label display mode
  // spriteSheetResolution: 2048, // resolution of the sprite sheet square
  // spriteSheetMaxSprites: 8     // number max of sprites
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
design = sigma.plugins.design(s, {
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

function updateGraph_(s, data) {
  // Calls API to return neighbouring nodes and edges, then updates graph.
  let update = {
    nodes: [],
    edges: []
  };

  // Wait until getNodes and getEdges complete
  Promise.all([
    getNodes(data).then(values =>
      {
        values.forEach( (n) => {
        if (!s.graph.nodes(n['id'])) {
          update.nodes.push(n);}
        });
      }),
    getEdges(data).then(values =>
      {
        values.forEach( (e) => {
          if (!s.graph.edges(e['id'])) {
            update.edges.push(e);}
        });
      }),
  ]).then(values => {
    // then update graph
    s.graph.read(update);
    // re-apply design
    design.deprecate();
    design.apply();
    // update activeState
    activeState.dropNodes();
    activeState.dropEdges();
    activeState.addNodes(data.id);
    activeState.addEdges(s.graph.adjacentEdges(data.id).map(i => i.id));
    // refresh graph
    s.refresh();
    updatePane(s.graph, filter);
  }).then(() => {
    let neighbours = s.graph.adjacentNodes(data.id);
    locate.nodes(neighbours.map(n => n.id));
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

/**
 * Bind events
  */
s.bind('clickNode', function(e) {
  // console.log(e.type, e.data.node.id, e.data.node.label, e.data.captor);
  if (activeState.nodes().includes(e.data.node)) {
    locate.center(locate_settings.zoomDef);
  } else {
    // TODO: this may call API for node which has previously been called - fix.
    updateGraph_(s, e.data.node);
  }
});

s.bind('rightClickStage', function() {
  locate.center(locate_settings.zoomDef);
});

// TODO: These are not bound together - therefore one does not update as another is used - intended?
_.$('min-degree').addEventListener("input", applyMinDegreeFilter);
_.$('min-year').addEventListener("input", applyMinYearFilter);

// s.bind('clickEdge doubleClickEdge rightClickEdge', function(e) {
//   console.log(e.type, e.data.edge, e.data.captor);
// });
// s.bind('clickStage doubleClickStage rightClickStage', function(e) {
//   console.log(e.type, e.data.captor);
// });
// s.bind('hovers', function(e) {
//   console.log(e.type, e.data.captor, e.data);
// });
