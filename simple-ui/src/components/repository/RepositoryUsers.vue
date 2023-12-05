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
  <q-dialog ref="dialogRef" style="min-width: 500px">
    <q-card class="q-pa-md">
        <q-input filled v-model="text" label="Share with..." lazy-rules>
          <template v-slot:append>
            <q-icon name="add" class="cursor-pointer" @click="shareRepo(repo, text)" />
          </template>
        </q-input>
      <q-scroll-area class="fit">
        <div class="q-pa-sm">
          <div v-for="n in 5" :key="n">Drawer {{ n }} / 50</div>
        </div>
      </q-scroll-area>
      <q-card-section class="column items-center">
        <div class="q-pa-md" style="min-width: 500px" v-if="copiedUsers.length > 0">
          <q-toolbar class="bg-primary text-white shadow-2">
            <q-toolbar-title>Contributors:</q-toolbar-title>
          </q-toolbar>

          <q-list bordered>
            <q-item v-for="contact in copiedUsers" :key="contact" class="q-my-sm" clickable v-ripple>
              <q-item-section avatar>
                <q-avatar color="primary" text-color="white">
                  {{ contact[0] }}
                </q-avatar>
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ contact }}</q-item-label>
              </q-item-section>

              <q-btn side push color="red" flat round icon="cancel" v-if="copiedUsers.indexOf(contact) != 0"
                @click="unshareRepo(repo, contact)">
              </q-btn>
              <p v-if="copiedUsers.indexOf(contact) == 0">owner</p>
            </q-item>
          </q-list>
        </div>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useDialogPluginComponent, useQuasar } from 'quasar';
import { api } from 'src/boot/axios';
import { Repository } from '../models';

const props = defineProps<{
  repo: Repository;
  repoUsers: string[];
}>();

defineEmits(useDialogPluginComponent.emitsObject);

const $q = useQuasar();
const { dialogRef, onDialogCancel } = useDialogPluginComponent();
let copiedUsers = ref(props.repoUsers);
let text = ref()

const shareRepo = async (repo: Repository, user: string) => {
  await api
    .post('/repositories/' + repo.id + '/share/' + user)
    .then((res) => {
      copiedUsers.value.push(res.data);
      onDialogCancel();
    })
    .catch((error) => $q.notify({ message: "Unable to share repository", type: 'negative' }));
};

const unshareRepo = async (repo: Repository, user: string) => {
  await api
    .post('/repositories/' + repo.id + '/unshare/' + user)
    .then((res) => {
      let index = copiedUsers.value.indexOf(res.data);
      if (index !== -1) {
        copiedUsers.value.splice(index, 1);
      }
      onDialogCancel();
    })
    .catch((error) => $q.notify({ message: "Unable to unshare repository", type: 'negative' }));
};
</script>
