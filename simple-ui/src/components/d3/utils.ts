import * as d3 from 'd3';
import { useCanvasStore } from 'src/stores/canvasStore';
import { useConfigStore } from 'src/stores/configStore';
import {
  D3_CONSTS,
  DataType,
  GenericCoords,
  PathCoords,
  PathElements,
  UIState,
} from './types';

export function isNameValid(name: string) {
  try {
    d3.select(`.node[data-id=${name}]`);
  } catch (_) {
    return false;
  }
  return true;
}

export function getEdgeName(elems: PathElements) {
  return `${elems.fromNode}-{out}-${elems.fromPort}|${elems.toNode}-{in}-${elems.toPort}`;
}

export function calculatePath(coords: PathCoords) {
  const path = d3.path();
  path.moveTo(coords.xFrom, coords.yFrom);
  path.bezierCurveTo(
    (coords.xFrom + coords.xTo) / 2,
    coords.yFrom,
    (coords.xFrom + coords.xTo) / 2,
    coords.yTo,
    coords.xTo,
    coords.yTo
  );
  return path.toString();
}

export function extractPathElems(path: SVGPathElement): PathElements {
  return {
    fromNode: path.dataset['fromParent'],
    fromPort: path.dataset['fromPort'],
    toNode: path.dataset['toParent'],
    toPort: path.dataset['toPort'],
  };
}

export function extractPathCoords(elems: PathElements): PathCoords {
  const fromParent = d3.select<SVGGElement, DataType>(
    '.node[data-id=' + elems.fromNode + ']'
  );
  const fromPort = d3.select(
    `circle[data-io=output][data-parent=${elems.fromNode}][data-name=${elems.fromPort}]`
  );
  const toParent = d3.select<SVGGElement, DataType>(
    '.node[data-id=' + elems.toNode + ']'
  );
  const toPort = d3.select(
    `circle[data-io=input][data-parent=${elems.toNode}][data-name=${elems.toPort}]`
  );
  return {
    xFrom: fromParent.datum().x + +fromPort.attr('cx'),
    yFrom: fromParent.datum().y + +fromPort.attr('cy'),
    xTo: toParent.datum().x + +toPort.attr('cx'),
    yTo: toParent.datum().y + +toPort.attr('cy'),
  };
}

export function portContainsPoint(c: SVGCircleElement, e: Event) {
  return (
    Math.pow(+c.getAttribute('cx') - d3.pointer(e, c)[0], 2) +
      Math.pow(+c.getAttribute('cy') - d3.pointer(e, c)[1], 2) <=
    D3_CONSTS.PORT_RADIUS * D3_CONSTS.PORT_RADIUS
  );
}

export function checkPorts(
  d3g: d3.Selection<Element, unknown, null, undefined>
) {
  d3g.selectAll<SVGCircleElement, unknown>('circle').each(function (this) {
    const fromOrTo = this.dataset['io'] == 'input' ? 'to' : 'from';
    const hasEdges = !d3
      .select<SVGPathElement, unknown>(
        `path[data-${fromOrTo}-parent=${this.dataset['parent']}][data-${fromOrTo}-port=${this.dataset['name']}]`
      )
      .empty();
    d3.select(this).classed('connected', hasEdges);
  });
}

export function calculateTextLength(
  d3g: d3.Selection<Element, unknown, null, undefined>,
  text: string,
  fontSize: string
) {
  const node = d3g.append('text').attr('font-size', fontSize).text(text).node();
  const length = node.getComputedTextLength();
  node.remove();
  return length;
}

export function extractTranslateCoords(transform: string): GenericCoords {
  const regex = /translate\((?<x>.+?)[, ]+(?<y>.+?)\)/gim;
  const res = regex.exec(transform);
  return { x: +res[1], y: +res[2] };
}

export function getNextNodeId(
  d3g: d3.Selection<Element, unknown, null, undefined>,
  nodeClass: string
) {
  let nodeId = '';
  for (let i = 1; true; i++) {
    nodeId = `${nodeClass}${i}`;
    if (d3g.select('.node[data-id=' + nodeId + ']').empty()) {
      break;
    }
  }

  return nodeId;
}

export function getUIState() {
  const canvasStore = useCanvasStore();
  const configStore = useConfigStore();

  return {
    nodes: [...canvasStore.canvasNodes.entries()],
    edges: [...canvasStore.canvasEdges.entries()],
    transform: canvasStore.canvasTransform,
    structures: [...configStore.nodeStructures.entries()],
    configs: [...configStore.nodeConfigs.entries()],
    anyConfigs: [...configStore.nodeAnyConfigs.entries()],
  } as UIState;
}

function setUIState(uiState: UIState) {
  const canvasStore = useCanvasStore();
  const configStore = useConfigStore();
  configStore.nodeStructures = new Map(uiState.structures);
  configStore.nodeConfigs = new Map(uiState.configs);
  configStore.nodeAnyConfigs = new Map(uiState.anyConfigs);
  canvasStore.canvasNodes = new Map(uiState.nodes);
  canvasStore.canvasEdges = new Map(uiState.edges);
  canvasStore.canvasTransform = uiState.transform;
}

export function loadUIFromFile(file: File) {
  return new Promise<boolean>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = () => {
      try {
        const uiState = JSON.parse(reader.result as string) as UIState;
        setUIState(uiState);
      } catch {
        resolve(false);
      }
      resolve(true);
    };
    reader.readAsText(file, 'utf8');
  });
}
