/*
 Copyright (C) 2023 Università degli Studi di Camerino.
 Authors: Alessandro Antinori, Rosario Capparuccia, Riccardo Coltrinari, Flavio Corradini, Marco Piangerelli, Barbara Re, Marco Scarpetta, Luca Mozzoni, Vincenzo Nucci

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { exportFile, Notify } from 'quasar';
import { useCanvasStore } from 'src/stores/canvasStore';
import { useConfigStore } from 'src/stores/configStore';
import { UIState } from './d3/types';
import { getUIState } from './d3/utils';
import { CustomNodeStructure } from './models';

export const getNodesConfig = () => {
  const canvasStore = useCanvasStore();
  const configStore = useConfigStore();
  return [...canvasStore.canvasNodes.keys()].map((nodeName: string) => {
    const nodePackage = canvasStore.canvasNodes.get(nodeName).package;
    const nodeConfig: { [index: string]: unknown } = {
      node_id: nodeName,
      node: nodePackage.includes('rain.nodes.custom.custom.CustomNode')
        ? 'rain.nodes.custom.custom.CustomNode'
        : nodePackage,
      parameters: Object.entries(configStore.nodeConfigs.get(nodeName)).reduce(
        (acc, value) =>
          value[1] != null ? Object.assign(acc, { [value[0]]: value[1] }) : acc,
        {}
      ),
    };

    if (
      (nodeConfig.node as string).includes(
        'rain.nodes.custom.custom.CustomNode'
      )
    ) {
      nodeConfig['function_name'] = (
        configStore.nodeStructures.get(nodePackage) as CustomNodeStructure
      ).function_name;
      nodeConfig['code'] = (
        configStore.nodeStructures.get(nodePackage) as CustomNodeStructure
      ).code;
    }

    nodeConfig['then'] = [...canvasStore.canvasEdges.values()]
      .filter((e) => e.fromNode == nodeName)
      .map((e) => {
        return {
          to_node: e.toNode,
          from_port: e.fromPort,
          to_port: e.toPort,
        };
      });

    return nodeConfig;
  });
};

export const getNodesRequirements = () => {
  const canvasStore = useCanvasStore();
  const configStore = useConfigStore();

  return [...canvasStore.canvasNodes.keys()]
    .map((nodeName) => canvasStore.canvasNodes.get(nodeName).package)
    .map((nodePackage) =>
      configStore.nodeStructures.get(nodePackage).tags['library'].toLowerCase()
    )
    .reduce(
      (acc, value) =>
        value != 'custom' && acc.indexOf(value) == -1 ? acc.concat(value) : acc,
      [] as string[]
    );
};

export const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'success':
      return 'green-6';
    case 'error':
      return 'red-6';
    case 'running':
      return 'primary'
    case 'revoked':
      return 'yellow-9';
    default:
      return 'grey';
  }
}

export const getConfig = () => {
  const config: { [index: string]: unknown } = {};
  config['pipeline_uid'] = Math.floor(100000 * Math.random()).toString();
  config['nodes'] = getNodesConfig();
  config['dependencies'] = getNodesRequirements();
  config['ui'] = getUIState();

  return config;
};

export const downloadUI = (uiState: UIState) => {
  const status = exportFile('ui.json', JSON.stringify(uiState), {
    mimeType: 'application/json',
    encoding: 'utf-8',
  });

  if (status) {
    Notify.create({
      message: 'UI file exported successfully',
      type: 'positive',
    });
  } else {
    Notify.create({
      message: 'Error while exporting UI file: ' + (status as Error).message,
      type: 'negative',
    });
  }
};

export const downloadPythonScript = (script: string) => {
  const status = exportFile('script.py', script, {
    encoding: 'utf-8',
  });

  if (status) {
    Notify.create({
      message: 'Python script exported successfully',
      type: 'positive',
    });
  } else {
    Notify.create({
      message:
        'Error while exporting Python script: ' + (status as Error).message,
      type: 'negative',
    });
  }
};


export const clearCanvas = () => {
  const canvasStore = useCanvasStore();
  const configStore = useConfigStore();
  canvasStore.clearCanvasEdges();
  canvasStore.clearCanvasNodes();
  configStore.clearNodeConfigs();
}