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
    <q-card class="q-pa-sm" style="display: flex; flex-direction: column; align-items: center">
      Files in folder: {{ folder.name }}
      <q-scroll-area class="fit">
        <div class="q-pa-sm">
          <div v-for="n in 5" :key="n">Drawer {{ n }} / 50</div>
        </div>
      </q-scroll-area>
      <q-card-section class="column items-center">
        <q-list bordered style="min-width: 500px">
          <q-item v-for="file in copiedFolderFiles" :key="file.id" outline>
            <q-item-section side>
              <div class="text-grey-8 q-gutter-xs">
                <q-btn size="12px" flat dense round icon="delete" title="Delete file" @click="deleteFile(file.id)" />
                <q-btn size="12px" flat dense round icon="download" title="Share folder" @click="downloadFile(file.id)" />
                <q-btn size="12px" flat dense round icon="content_copy" @click="copyID(file.id)" />
              </div>
            </q-item-section>
            <q-item-section>
              <q-item-label class="text-weight-medium">{{ displayFileName(file.name) }}</q-item-label>
              <q-item-label caption lines="1">{{ file.created_at }}</q-item-label>
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
import { useFolderStore } from 'src/stores/folderStore';
import { ref, onMounted, onUnmounted, inject, watch } from 'vue';

const props = defineProps<{
  folder: Folder;
}>();

defineEmits(useDialogPluginComponent.emitsObject);
const folderStore = useFolderStore()
const $q = useQuasar();
const { dialogRef, onDialogCancel } = useDialogPluginComponent();

// NB: this has to be done because the files listed in a folder 
// are returned as string instead of an array of ids
// TODO: fix in a more robust way
let folderFilesString: string = props.folder.files.toString().replace(/^'|'$/g, '')
const folderFilesArray: string[] = folderFilesString.slice(1, -1).split(', ')
const copiedFolderFiles = ref(Array.from(folderFilesArray, (file: string) => {
  return folderStore.files.get(file.slice(1, -1))
}) as LocalFile[]);

// TODO: Update file list when file is updated
// watch(
//   () => folderStore.$state,
//   async () => {
//     folderStore.folders.get(props.folder.id).files.forEach((file) => {
//       copiedFolderFiles.value.push(folderStore.files.get(file)) 
//     })
//   },
//   { deep: true }
// );

const copyID = (text: string) => {
  copyToClipboard(text)
    .then(() => {
      $q.notify({ message: "File ID copied to clipboard!", type: 'positive' })
    })
}

const displayFileName = (fileName: string) => {
  const maxLength = 50;
  if (fileName.length <= maxLength)
    return fileName;
  const [nameWithoutExtension, fileExtension] = fileName.split('.');
  const shortenedName = nameWithoutExtension.substring(0, maxLength - 3) + '...';
  const shortenedFileName = shortenedName + ' ' + fileExtension;
  return shortenedFileName;
}

const downloadFile = async (fileId: string) => {
  await api
    .get(`folders/files/${fileId}`)
    .then((res) => {
      const status = exportFile(res.data.name, res.data.content, {
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

const deleteFile = async (fileId: string) => {
  const file: LocalFile = folderStore.files.get(fileId)
  await api
    .delete<LocalFile>(`folders/${props.folder.id}/files/${file.id}`)
    .then(() => {
      folderStore.files.delete(fileId)
      if (copiedFolderFiles.value.length == 0) {
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
