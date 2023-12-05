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
  <div ref="container">
    <q-item class="badge" v-if="monitorStore.execution != null">
      <q-item-section avatar>
        <q-avatar :color="getStatusColor(monitorStore.execution.status)" :class="{ 'blink-animation': isExecutionRunning() }"  size="25px">
        </q-avatar>
      </q-item-section>
      <q-item-section>
        <q-item-label>{{ monitorStore.execution.name }}</q-item-label>
        <q-item-label caption lines="1">{{ monitorStore.execution.status }}</q-item-label>
      </q-item-section>
      <q-item-section top side>
        <div class="text-grey-8 q-gutter-xs">
          <q-btn class="gt-xs" size="16px" flat dense round icon="upload" @click.stop="reloadUI(monitorStore.execution.id)" />
          <q-btn v-if="!isExecutionRunning()" class="gt-xs" size="16px" flat dense round icon="delete" @click.stop="deleteExecution(monitorStore.execution.id)" />
          <q-btn v-else class="gt-xs" size="16px" flat dense round icon="stop" @click.stop="stopExecution(monitorStore.execution.id)" />
        </div>
        <div class="text-grey-8 q-gutter-xs">
        </div>
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
import { Ref, ref, watch, inject } from 'vue';
import { QInput } from 'quasar';
import { useMonitorStore } from '../../stores/monitorStore'
import { api } from '../../boot/axios';
import { useQuasar } from 'quasar';
import { getStatusColor } from '../utils';
import { useCanvasStore } from 'src/stores/canvasStore';
import { useExecutionStore } from 'src/stores/executionStore';
import { useRouter } from 'vue-router';

const router = useRouter();
const $q = useQuasar();
const executionStore = useExecutionStore()
const container: Ref<Element> = ref(null);
const input: Ref<QInput> = ref(null);
const logText = ref('');
const monitorStore = useMonitorStore();
const autoScroll = ref(false);
let openLeftDrawer: () => void = inject('openLeftDrawer')

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

const isExecutionRunning = () => {
  if (monitorStore.execution.status == 'Running' || monitorStore.execution.status == 'Pending')
    return true
  else return false
}

const reloadUI = async (executionId: string) => {
  await api
    .get<string>('/execution/' + executionId + '/info/ui')
    .then((value) => {
      sessionStorage.setItem('canvasState', value.data)
      router.push({name: 'canvas'})
    })
    .catch(() => 
      $q.notify({
        message: 'Unable to load execution UI!',
        type: 'negative',
      })
    );
}

const deleteExecution = async (executionId: string) => {
  await api
  .delete('/execution/' + executionId + '/info')
  .then(() => {
    openLeftDrawer()
    monitorStore.$reset()
    executionStore.executionsMap.delete(executionId)
  })
  .catch(() => {
    $q.notify({
      message: 'Unable to delete execution info!',
      type: 'negative',
    });
  });
}

const stopExecution = async (executionId: string) => {
  await api
  .post('/execution/' + executionId + '/revoke')
  .then()
  .catch(() => {
    $q.notify({
      message: 'Unable to stop execution!',
      type: 'negative',
    });
  });
}

const updateTextAndScroll = (line: string) => {
  logText.value += line;
  if (!autoScroll.value)
    return

  container.value.scrollIntoView(false);
  input.value.getNativeElement().scrollIntoView(false);
};
</script>

<style scoped>
@keyframes blink {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

.blink-animation {
  animation: blink 1s infinite;
}

.badge {
  padding-top: 15px;
}
</style>
