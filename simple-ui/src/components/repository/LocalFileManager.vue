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
    <q-list bordered>
        <q-item-label header>Folders</q-item-label>

        <q-item v-for="folder in folderStore.folders.values()" :key="folder.id">
            <q-item-section avatar top>
                <q-btn size="12px" outline icon="folder_open" label="Open" title="List folder content"
                    @click="openFolderDialog(folder)" data-cy="openRepositoryDialog" />
            </q-item-section>

            <q-item-section>
                <q-item-label lines="1">
                    <span class="text-weight-medium">{{ folder.name }}</span>
                </q-item-label>
            </q-item-section>

            <q-item-section v-if="folderStore.currentFolder == folder.id" side top>
                <div>
                    <q-icon size="24px" name="done"></q-icon>
                    Use by default
                </div>
            </q-item-section>
            <q-item-section top side>
                <div class="text-grey-8 q-gutter-xs">
                    <q-btn size="12px" flat dense round icon="content_copy" @click="copyID(folder.id)" />
                    <q-btn size="12px" flat dense round icon="share" v-if="folder.owner == true" title="Share folder"
                        @click="openUsersDialog(folder)" data-cy="deleteRepo" />
                    <q-btn size="12px" flat dense round icon="delete" title="Delete folder" v-if="folder.owner == true"
                        @click="deleteFolder(folder)" data-cy="deleteRepo" />
                    <q-btn v-if="folderStore.currentFolder != folder.id" size="12px" flat dense round icon="done"
                        title="Mark as Default" @click="markAsDefault(folder)" data-cy="markAsDefault" />
                </div>
            </q-item-section>
        </q-item>
    </q-list>
    <q-btn icon="add" outline @click="addFolder" data-cy="addRepo"></q-btn>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useQuasar, copyToClipboard } from 'quasar';
import { useFolderStore } from 'stores/folderStore';
import { api } from '../../boot/axios';
import { Folder, LocalFile } from '../models';
import FolderDialog from './FolderDialog.vue';
import FolderUsers from './FolderUsers.vue';
import { AxiosError, AxiosResponse } from 'axios';

const $q = useQuasar();
const folderStore = useFolderStore();

onMounted(async () => {
    api
        .get<Folder[]>('/folders')
        .then((res) => {
            folderStore.folders = new Map<string, Folder>();
            res.data.forEach((repo: Folder) => folderStore.folders.set(repo.id, repo));
            if (folderStore.folders.size > 0) {
                folderStore.currentFolder = [...folderStore.folders.values()][0].id;
            }
        })
        .catch((error: AxiosError) => {
            $q.notify({ message: "Unable to load folders", type: 'negative' });
        });
});

const copyID = (text: string) => {
    copyToClipboard(text)
        .then(() => {
            $q.notify({ message: "Folder ID copied to clipboard!", type: 'positive' })
        })
}

const addFolder = () => {
    $q.dialog({
        title: 'Add a new folder',
        message: 'What is the new name of the folder?',
        prompt: {
            model: '',
            isValid: (name) => {
                return name.trim() != '' && !folderStore.folders.has(name.trim());
            },
            type: 'text',
            outlined: true,
        },
        cancel: true,
    }).onOk((folderName) => {
        api
            .post('/folders/' + folderName)
            .then(() => {
                folderStore.folders.set(folderName, { id: folderName, name: folderName, owner: true, files: [] });
                if (folderStore.folders.size == 1) {
                    folderStore.currentFolder = [...folderStore.folders.values()][0].name;
                }
            })
            .catch((error) => $q.notify({ message: error, type: 'negative' }));
    });
};

const deleteFolder = (folder: Folder) => {
    $q.dialog({
        title: 'Delete a folder',
        message:
            'Are you sure you want to delete the folder: ' +
            folder.name +
            '?',
        cancel: true,
    }).onOk(() => {
        api
            .delete('/folders/' + folder.id)
            .then(() => {
                folderStore.folders.delete(folder.id);
                if (folderStore.folders.size == 1) {
                    folderStore.currentFolder = [...folderStore.folders.values()][0].name;
                }
                if (folderStore.folders.size == 0) {
                    folderStore.currentFolder = null;
                }
            })
            .catch((error) => $q.notify({ message: error, type: 'negative' }));
    });
};

const markAsDefault = (folder: Folder) => {
    $q.dialog({
        title: 'Confirm',
        message:
            'Are you sure you want to mark the folder: ' +
            folder.name +
            ' as default?',
        cancel: true,
    }).onOk(() => {
        folderStore.currentFolder = folder.id;
    });
};

const openFolderDialog = async (folder: Folder) => {
    await api
        .get('/folders/' + folder.id)
        .then((res) => {
            if (res.data.length == 0) {
                $q.notify({
                    message: 'No files available in the folder: ' + folder.name,
                    type: 'negative',
                });
            } else {
                res.data.forEach((file: LocalFile) => {
                    folderStore.files.set(file.id, file)
                });
                $q.dialog({
                    component: FolderDialog,
                    componentProps: { folder: folder },
                });
            }
        })
        .catch()
};

const openUsersDialog = async (folder: Folder) => {
    await api
        .get('/folders/' + folder.id + '/users')
        .then((res: AxiosResponse) => {
            const folderUsers: string[] = res.data;
            $q.dialog({
                component: FolderUsers,
                componentProps: { folder: folder, folderUsers: folderUsers },
            });
        })
        .catch((err: AxiosError) => {
            $q.notify({
                message: (err.response.data as { message: string }).message,
                type: 'negative',
            });
        });
};
</script>
