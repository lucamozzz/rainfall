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
  <q-dialog ref="dialogRef">
    <q-card class="q-pa-md" style="display: flex; flex-direction: column; align-items: center">
      Files in folder: {{ folder.name }}
      <q-scroll-area class="fit">
        <div class="q-pa-sm">
          <div v-for="n in 5" :key="n">Drawer {{ n }} / 50</div>
        </div>
      </q-scroll-area>
      <q-card-section class="column items-center">
        <q-list bordered style="min-width: 500px">
          <q-item v-for="file in folderFiles" :key="file.name" outline>
            <q-item-section side>
              <div class="text-grey-8 q-gutter-xs">
                <q-btn size="12px" flat dense round icon="delete" title="Delete file"
                  @click="onDeleteFile(file.name)" />
                <q-btn size="12px" flat dense round icon="download" title="Download file"
                  @click="downloadFile(file.name)" />
                <q-btn size="12px" v-if="file.name.endsWith('.csv')" flat dense round icon="visibility"
                  title="View file" @click="visualizeFile(file.name)" />
              </div>
            </q-item-section>
            <q-item-section @click="copyID(folder.name + '/' + file)" class="cursor-pointer">
              <q-item-label lines="1" class="text-weight-medium">{{ file.name }}</q-item-label>
              <q-item-label lines="1" :caption="true" class="text-weight-medium">{{ file.created_at + ' • ' + file.size
                }}</q-item-label>
            </q-item-section>
            <q-separator />
          </q-item>
        </q-list>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { useDialogPluginComponent, useQuasar, copyToClipboard, exportFile } from 'quasar';
import { api } from 'src/boot/axios';
import { AxiosError } from 'axios';
import { Folder, LocalFile } from '../models';
import { ref } from 'vue';
import { csvToHtmlPage } from '../visuals';

const props = defineProps<{
  folder: Folder;
  files: LocalFile[];
}>();

defineEmits(useDialogPluginComponent.emitsObject);
const $q = useQuasar();
const { dialogRef, onDialogCancel } = useDialogPluginComponent();
const folderFiles = ref(props.files.slice());

const copyID = (text: string) => {
  copyToClipboard(text)
    .then(() => {
      $q.notify({ message: 'File name copied to clipboard!', type: 'positive' })
    })
}

const downloadFile = async (fileName: string) => {
  await api
    .get(`folders/${props.folder.name}/${fileName}`)
    .then((res) => {
      const status = exportFile(fileName, res.data, {
        encoding: 'utf-8',
      });
      if (status) {
        $q.notify({
          message: 'File downloaded successfully',
          type: 'positive',
        });
      } else {
        $q.notify({
          message:
            'Error while downloading file: ' + (status as Error).message,
          type: 'negative',
        });
      }
    })
    .catch((err: AxiosError) => {
      $q.notify({
        message: (err.response.data as { message: string }).message,
        type: 'negative',
      });
    });
};

const visualizeFile = async (fileName: string) => {
  if (fileName.split('.').pop() != 'csv')
    $q.notify({
      message: 'Not a CSV file',
      type: 'negative',
    });
  else await api
    .get(`folders/${props.folder.name}/${fileName}`)
    .then((res) => {
      let fileContent = res.data;
      fileContent = csvToHtmlPage(res.data, fileName);
      const fileBlob = new Blob([fileContent], { type: 'text/html;charset=utf-8' });
      const fileUrl = URL.createObjectURL(fileBlob);
      window.open(fileUrl, '_blank');
      setTimeout(() => URL.revokeObjectURL(fileUrl), 10000);
    })
    .catch((err: AxiosError) => {
      $q.notify({
        message: (err.response.data as { message: string }).message,
        type: 'negative',
      });
    });
};

const onDeleteFile = async (file: string) => {
  await api
    .delete<LocalFile>(`folders/${props.folder.name}/files/${file}`)
    .then(() => {
      folderFiles.value.splice(
        folderFiles.value.findIndex((fileObj) => fileObj.name == file),
        1
      );
      if (folderFiles.value.length == 0) {
        onDialogCancel();
      }
    })
    .catch((err: AxiosError) => {
      $q.notify({
        message: (err.response.data as { message: string }).message,
        type: 'negative',
      });
    });
};
</script>
