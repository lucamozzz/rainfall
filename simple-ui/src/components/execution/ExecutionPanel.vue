<!--
 Copyright (C) 2023 Università degli Studi di Camerino and Sigma S.p.A.
 Authors: Alessandro Antinori, Rosario Capparuccia, Riccardo Coltrinari, Flavio Corradini, Marco Piangerelli, Barbara Re, Marco Scarpetta

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 -->

<template>
  <div ref="container">
    <!-- <q-item v-if="monitorStore.execution == null">
      <q-item-section>
        <q-item-section>
          Select an execution from the side menu...
        </q-item-section>
      </q-item-section>
    </q-item> -->
    <q-item class="badge" v-if="monitorStore.execution != null">
      <q-item-section avatar>
        <q-avatar :color="getStatusColor(monitorStore.execution.status)" size="25px">
        </q-avatar>
      </q-item-section>
      <q-item-section>
        <q-item-label>{{ monitorStore.execution.id }}</q-item-label>
        <q-item-label caption lines="1">{{ monitorStore.execution.status }}</q-item-label>
      </q-item-section>
    </q-item>

    <q-input
      ref="input"
      class="q-pa-md"
      v-model="logText"
      autogrow
      readonly
      outlined
      data-cy="log"
    ></q-input>
  </div>
</template>

<script setup lang="ts">
import { Ref, ref, watch } from 'vue';
import { QInput, useQuasar } from 'quasar';
import { useMonitorStore } from '../../stores/monitorStore'

const container: Ref<Element> = ref(null);
const input: Ref<QInput> = ref(null);
const logText = ref('');
const monitorStore = useMonitorStore();
const autoScroll = ref(true);

watch(
  () => monitorStore.$state,
  async (state) => {
    logText.value = ''
    if (state.execution){
      state.execution.logs.forEach((log) => {        
        log = log + (log.endsWith('\n') ? '' : '\n');
        updateTextAndScroll(log);
      })
    }
  },
  { deep: true }
);

const updateTextAndScroll = (line: string) => {
  logText.value += line;
  if (!autoScroll.value)
    return

  container.value.scrollIntoView(false);
  input.value.getNativeElement().scrollIntoView(false);
};

const getStatusColor = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'success':
      return 'green-6';
    case 'error':
      return 'red-6';
    case 'running':
      return 'yellow-9';
    default:
      return 'grey';
  }
}
</script>

<style scoped>
.badge {
  padding-top: 15px;
}
</style>
