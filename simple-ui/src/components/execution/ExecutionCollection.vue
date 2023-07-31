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
  <div class="q-pa-md" style="max-width: 350px">

    <q-list >
      <q-item v-for="execution in executionInfoArray" :key="execution.id" class="q-my-sm" clickable v-ripple @click="selectExecution(execution.id)">
        <q-item-section avatar>
          <q-avatar :color="getStatusColor(execution.status)" size="20px">
          </q-avatar>
        </q-item-section>
        <q-item-section>
          <q-item-label>{{ execution.id }}</q-item-label>
          <q-item-label caption lines="1">{{ execution.status }}</q-item-label>
        </q-item-section>
        <q-item-section top side>
          <div class="text-grey-8 q-gutter-xs">
            <q-btn class="gt-xs" size="12px" flat dense round icon="delete" @click.stop="deleteExecution(execution.id)" />
          </div>
        </q-item-section>
      </q-item>
      <q-item v-if="executionInfoArray.length === 0">
        <q-item-section>
          <q-item-section>
            <q-btn color="primary" @click="() => router.push({ name: 'canvas' })">Create pipeline</q-btn>
          </q-item-section>
        </q-item-section>
      </q-item>
    </q-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { api } from '../../boot/axios';
import { ExecutionInfo } from '../models'
import { useMonitorStore } from '../../stores/monitorStore'
import { useQuasar } from 'quasar';
import { useCanvasStore } from 'src/stores/canvasStore';
import { useRouter } from 'vue-router';

const $q = useQuasar();
const router = useRouter();
const canvasStore = useCanvasStore()
const monitorStore = useMonitorStore();
let eventSource: EventSource
let executionInfoArray = ref([])
let executionInfoMap = new Map<string, string>()

onMounted(async () => {
  await getExecutions()
  if (executionInfoArray.value.length != 0) {
    await selectExecution(executionInfoArray.value[0].id)
  }
});

const getExecutions = async () => {
  await api
    .get<ExecutionInfo[]>('/execution/statuses')
    .then((value) => {
      executionInfoMap = value.data.reduce((map, obj) => {
        map.set(obj.id, obj.status);
        return map;
      }, new Map<string, string>());
      executionInfoArray.value = getExecutionsArray()
    })
    .catch(() => {
      $q.notify({
        message: 'Unable to load execution statuses!',
        type: 'negative',
      });
    })

    eventSource = new EventSource(process.env.BACKEND_URL + "/api/v1/execution/watch");  
    eventSource.onmessage = (event) => {
      const executionUpdate: ExecutionInfo = JSON.parse(event.data)
      executionInfoMap.set(executionUpdate.id, executionUpdate.status)
      executionInfoArray.value = getExecutionsArray()
      if (monitorStore.execution && monitorStore.execution.id == executionUpdate.id) {
        monitorStore.execution.status = executionUpdate.status
      }
    };
    eventSource.onerror = (error) => {
      console.error("SSE error:", error);
      eventSource.close()
    };
};

const getExecutionsArray = () => {
  return Array.from(executionInfoMap.entries())
        .map(([id, status]) => ({
          id: id,
          status: status,
        })).reverse()
}

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

  eventSource = new EventSource(process.env.BACKEND_URL + "/api/v1/execution/watch/" + executionId);  
  eventSource.onmessage = (event) => {
    // TODO: fix API endpoint that returns string array
    let update: { id: string, logs: string | string[] } = JSON.parse(event.data)
    if (typeof update.logs === 'string')
      monitorStore.execution.logs.push(update.logs)
    else
      monitorStore.execution.logs.push(update.logs[0])
  };
  
  // TODO: close connection when no content
  eventSource.onerror = (error) => {
    // console.error("SSE error:", error);
    eventSource.close()
  };
};

const deleteExecution = (executionId: string) => {
  api
  .delete('/execution/' + executionId + '/info')
  .then(() => {
    canvasStore.clearCanvasEdges()
    canvasStore.clearCanvasNodes()
    executionInfoMap.delete(executionId)
    executionInfoArray.value = getExecutionsArray()
  })
  .catch(() => {
    $q.notify({
      message: 'Unable to delete execution info!',
      type: 'negative',
    });
  });
}

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

onUnmounted(() => {
    eventSource.close()
    monitorStore.$reset()
  }
);

</script>