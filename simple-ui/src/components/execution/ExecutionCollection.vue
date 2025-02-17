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
  <div class="q-pa-md" style="max-width: 350px">

    <q-list>
      <q-item v-for="execution in executionInfoArray" :key="execution.id" class="q-my-sm" clickable v-ripple
        @click="selectExecution(execution.id)">
        <q-item-section avatar>
          <q-avatar :color="getStatusColor(execution.status)"
            :class="{ 'blink-animation': isExecutionRunning(execution.id) }" size="20px">
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ execution.name }}</q-item-label>
          <q-item-label caption lines="1">{{ execution.status }}</q-item-label>
        </q-item-section>
      </q-item>
      <div v-if="executionInfoArray.length === 0">
        <q-item>
          <q-item-section>
            <q-btn color="primary" @click="() => router.push({ name: 'canvas' })">Create new pipeline</q-btn>
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section>
            <q-btn color="primary" @click="() => router.push({ name: 'import_export' })">Load from repository</q-btn>
          </q-item-section>
        </q-item>
      </div>
    </q-list>
  </div>
</template>

<script setup lang="ts">
import { useQuasar } from 'quasar';
import { api } from '../../boot/axios';
import { ExecutionInfo } from '../models'
import { useMonitorStore } from '../../stores/monitorStore'
import { useExecutionStore } from 'src/stores/executionStore';
import { ref, onMounted, onUnmounted, inject, watch } from 'vue';
import { getStatusColor } from '../utils';
import { useRouter } from 'vue-router';

const $q = useQuasar();
const router = useRouter();
const executionStore = useExecutionStore()
const monitorStore = useMonitorStore();
let executionEventSource: EventSource
let monitorEventSource: EventSource
let executionInfoArray = ref([] as ExecutionInfo[])

onMounted(async () => {
  await getExecutions()
  openLeftDrawer()
});

let openLeftDrawer: () => void = inject('openLeftDrawer')

watch(
  () => monitorStore.$state,
  async (state) => {
    if (!state.execution) {
      openLeftDrawer()
    }
  },
  { deep: true }
);

watch(
  () => executionStore.$state,
  async () => {
    executionInfoArray.value = executionStore.getExecutionsArray()
  },
  { deep: true }
);

const isExecutionRunning = (executionId: string) => {
  if (executionStore.executionsMap.get(executionId).status == 'Running' || executionStore.executionsMap.get(executionId).status == 'Pending')
    return true
  else return false
}

const getExecutions = async () => {
  await api
    .get<ExecutionInfo[]>('/execution/info')
    .then((value) => {
      executionStore.executionsMap = value.data.reduce((map, obj) => {
        map.set(obj.id, obj);
        return map;
      }, new Map<string, ExecutionInfo>());
      executionInfoArray.value = executionStore.getExecutionsArray()

    })
    .catch(() => {
      $q.notify({
        message: 'Unable to load executions!',
        type: 'negative',
      });
    })

  executionEventSource = new EventSource(process.env.BACKEND_URL + '/api/v1/execution/watch');
  executionEventSource.onmessage = (event) => {
    let data = event.data
    if (data != 'None') {
      if (data.startsWith('data: '))
        data = data.slice(5)
      const executionUpdate: ExecutionInfo = JSON.parse(data)
      let executionInfo: ExecutionInfo = executionStore.executionsMap.get(executionUpdate.id)
      if (executionInfo) {
        executionInfo.status = executionUpdate.status
        executionStore.executionsMap.set(executionUpdate.id, executionInfo)
      }
      if (monitorStore.execution && monitorStore.execution.id == executionUpdate.id) {
        monitorStore.execution.status = executionUpdate.status
      }
    };
  }

  executionEventSource.onerror = (error) => {
    console.error('SSE error:', error);
    executionEventSource.close()
  };
};

const selectExecution = async (executionId: string) => {
  await api
    .get<ExecutionInfo>('/execution/' + executionId + '/info')
    .then((value) => monitorStore.setExecution(value.data as ExecutionInfo))
    .catch(() =>
      $q.notify({
        message: 'Unable to load execution info!',
        type: 'negative',
      })
    );

  monitorEventSource = new EventSource(process.env.BACKEND_URL + '/api/v1/execution/watch/' + executionId);
  monitorEventSource.onmessage = (event) => {
    let data: string = event.data
    if (data != 'None') {
      // TODO: fix API endpoint that returns string array
      if (data.startsWith('data: '))
        data = data.slice(5)
      let update: { id: string, logs: string | string[] | null, status: string | null } = JSON.parse(data)
      if (update.logs != null) {
        if (typeof update.logs === 'string')
          monitorStore.execution.logs.push(update.logs)
        else
          monitorStore.execution.logs.push(update.logs[0])
      } else {
        monitorStore.execution.status = update.status
      }
    };
  }

  monitorEventSource.onerror = () => {
    // console.error("SSE error:", error);
    monitorEventSource.close()
  };
};

onUnmounted(() => {
  if (executionEventSource)
    executionEventSource.close()
  if (monitorEventSource)
    monitorEventSource.close()
  monitorStore.$reset()
}
);

</script>


<style>
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
</style>