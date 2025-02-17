<!--
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
 -->

<template>
  <q-item-label header class="row justify-center">Nodes</q-item-label>

  <div class="row justify-center no-wrap">
    <q-btn-toggle
      style="border: 1px solid #1976d2"
      no-caps
      rounded
      unelevated
      toggle-color="primary"
      color="white"
      text-color="primary"
      v-model="currentViewMode"
      :options="[
        { value: ViewMode.TYPE, slot: 'type' },
        { value: ViewMode.LIBRARY, slot: 'library' },
      ]"
      @update:model-value="organizeNodesByViewMode()"
      data-cy="viewToggle"
    >
      <template v-slot:library>
        <div class="row items-center no-wrap">
          <div class="text-center">Library</div>
          <q-icon right name="sort" />
        </div>
      </template>

      <template v-slot:type>
        <div class="row items-center no-wrap">
          <q-icon left name="sort" />
          <div class="text-center">Type</div>
        </div>
      </template>
    </q-btn-toggle>
  </div>

  <div>
    <q-input
      class="q-pa-sm"
      dense
      hide-bottom-space
      rounded
      outlined
      clearable
      debounce="500"
      v-model="filter"
      label="Search nodes"
      @clear="expandTree(false)"
      @update:model-value="$event !== '' ? expandTree(true) : expandTree(false)"
      data-cy="searchBar"
    >
      <template v-slot:append>
        <q-icon name="search" />
      </template>
    </q-input>
  </div>

  <q-tree
    ref="tree"
    :nodes="organizedNodes"
    node-key="id"
    :filter="filter"
    :filter-method="filterMethod"
  >
    <template v-slot:default-header="prop">
      <div class="row items-center">
        <div
          v-if="prop.node.header === 'root'"
          class="text-weight-bold text-primary"
          data-cy="treeRoot"
        >
          <q-icon
            name="settings_applications"
            color="primary"
            size="28px"
            class="q-mr-sm"
          />
          {{prop.node.label}}
        </div>
        <div
          v-else
          :draggable="true"
          @dragstart="$event.dataTransfer.setData('text', prop.node.id)"
          style="border: 2px solid gray; padding: 5px"
          data-cy="treeNode"
        >
          <q-tooltip anchor="center right" self="center right" :delay="750">
            {{ configStore.nodeStructures.get(prop.node.id).description }}
          </q-tooltip>
          <q-icon name="share" color="orange" size="28px" class="q-mr-sm" />

          {{ prop.node.label }}
        </div>
      </div>
    </template>
  </q-tree>
</template>

<script setup lang="ts">
import { ref, Ref, nextTick, watch } from 'vue';
import { QTree, useQuasar } from 'quasar';
import { api } from '../boot/axios';
import { QTreeNode, SimpleNodeStructure } from './models';
import { useConfigStore } from 'stores/configStore';

// TODO: manage API call failure (e.g. show a 'Pull to refresh')
const $q = useQuasar();
const configStore = useConfigStore();
const tree: Ref<QTree> = ref(null);
enum ViewMode {
  LIBRARY,
  TYPE,
}
const currentViewMode = ref(ViewMode.TYPE);
const filter = ref('');
const nodes = ref([] as QTreeNode[]);
const organizedNodes = ref([]);
let libraries = [] as string[];
let types = [] as string[];

watch(
  () => configStore.nodeStructures,
  (newVal) => {
    nodes.value = [];
    setNodeStructures([...newVal.values()]);
  },
  { deep: true }
);

const getNodes = () => {
  api
    .get<SimpleNodeStructure[]>('/nodes')
    .then((value) => {
      const tempCustomNodes = [...configStore.nodeStructures.values()].filter(
        (n) => n.package.includes('rain.nodes.custom.custom.CustomNode')
      );
      configStore.setNodeStructures(value.data);
      tempCustomNodes.forEach((n) => configStore.addNodeStructure(n));
    })
    .catch(() => {
      $q.notify({
        message: 'Unable to load nodes!',
        type: 'negative',
      });
    });
};

getNodes();

const setNodeStructures = (structures: SimpleNodeStructure[]) => {
  libraries = [...new Set(structures.map((n) => n.tags.library))];
  types = [...new Set(structures.map((n) => n.tags.type))];
  structures.forEach((v) => {
    nodes.value.push({
      label: v.clazz,
      selectable: true,
      body: 'story',
      story: {
        library: v.tags.library,
        type: v.tags.type,
      },
      id: v.package,
    });
  });
  organizeNodesByViewMode();
};

const organizeNodesByViewMode = () => {
  const treeData = new Map<string, QTreeNode[]>();
  if (currentViewMode.value == ViewMode.LIBRARY) {
    libraries.forEach((l) => treeData.set(l, []));
  } else {
    types.forEach((t) => treeData.set(t, []));
  }
  nodes.value.forEach((n) => {
    if (currentViewMode.value == ViewMode.LIBRARY) {
      treeData.get(n.story.library).push(n);
    } else {
      treeData.get(n.story.type).push(n);
    }
  });
  const organizedTreeData = [...treeData.keys()].map((k) => ({
    // label: k,
    label: k.split('\n')[0],
    selectable: false,
    header: 'root',
    id: k,
    children: treeData.get(k),
  }));
  organizedNodes.value = organizedTreeData;
  if (filter.value != null && filter.value.trim() !== '') {
    void nextTick(() => tree.value.expandAll());
  }
};

const filterMethod = (node: QTreeNode, filter: string) => {
  if (filter == null || filter.trim() === '') {
    return false;
  }
  if (node.header) {
    return false;
  }
  return node.label.toLowerCase().indexOf(filter.toLowerCase()) > -1;
};

const expandTree = (expand: boolean) => {
  if (expand) {
    tree.value.expandAll();
  } else {
    tree.value.collapseAll();
  }
};
</script>
