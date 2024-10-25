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
  <q-page padding>
    <div class="q-pa-md q-gutter-sm">
      <q-btn icon="file_download" color="secondary" label="Save DataFlow" @click="saveDataFlow" :disable="isUploading"
        data-cy="saveDataflow">
      </q-btn>
      <repository-manager></repository-manager>
    </div>

    <q-separator spaced=""></q-separator>
    <q-dialog v-model="isUploading" persistent no-backdrop-dismiss>
      <q-spinner color="primary" size="100px" />
    </q-dialog>
    <div class="q-pa-md q-gutter-sm">
      <q-file ref="filePicker" style="display: none" accept=".csv,.xes" :loading="isUploading" v-model="file"
        max-file-size="104857600" @update:model-value="loadFile">
      </q-file>
      <q-btn icon="file_upload" color="secondary" label="Upload File" @click="filePicker.pickFiles()"
        :disable="isUploading" />
      <local-file-manager></local-file-manager>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { api } from '../boot/axios';
import { useQuasar, QFile } from 'quasar';
import { getConfig } from 'src/components/utils';
import RepositoryManager from 'src/components/repository/RepositoryManager.vue';
import LocalFileManager from 'src/components/repository/LocalFileManager.vue';
import { useRepoStore } from 'src/stores/repoStore';
import { Ref, ref } from 'vue';
import { useFolderStore } from 'src/stores/folderStore';

const $q = useQuasar();
const repoStore = useRepoStore();
const folderStore = useFolderStore();
const filePicker: Ref<QFile> = ref(null);
const file: Ref<File> = ref(null);
const isUploading: Ref<boolean> = ref(false);

const saveDataFlow = async () => {
  const config = getConfig();
  let canvasState = sessionStorage.getItem('canvasState')
  if (repoStore.currentRepo == null || canvasState == null) {
    $q.notify({
      message:
        'Unable to save dataflow!',
      type: 'negative',
    });
    return;
  }
  config['ui'] = JSON.parse(canvasState)
  config['repository'] = repoStore.currentRepo;

  await api
    .post('/config', config)
    .then((res) => {
      $q.notify({
        message:
          'Dataflow: ' +
          res.data['_id'] +
          ' saved successfully!',
        type: 'positive',
      });
    })
    .catch((error: Error) => {
      $q.notify({
        message: error.message,
        type: 'negative',
      });
    });
};

const loadFile = async () => {
  isUploading.value = true;
  return await new Promise<boolean>((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = async () => {
      try {
        const uploadedFile = reader.result as string;
        await api.post('/folders/file', { name: file.value.name, content: uploadedFile, folder: folderStore.currentFolder })
          .then(() => {
            $q.notify({
              message: 'File uploaded successfully!',
              type: 'positive',
            });
            resolve(true);
          })
          .catch((error) => {
            console.error(error);
            $q.notify({
              message: 'File upload failed!',
              type: 'negative',
            });
            resolve(false);
          });
      } catch (error) {
        console.error(error);
        $q.notify({
          message: 'Error processing the file!',
          type: 'negative',
        });
        resolve(false);
      } finally {
        isUploading.value = false;
        file.value = null;
      }
    };
    reader.readAsText(file.value, 'utf8');
  });
};
</script>