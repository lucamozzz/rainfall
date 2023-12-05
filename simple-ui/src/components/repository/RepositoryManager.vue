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
  <q-list bordered>
    <q-item-label header>Repositories</q-item-label>

    <q-item
      v-for="repo in repoStore.repos.values()"
      :key="repo.id"
      data-cy="repository"
    >
      <q-item-section avatar top>
        <q-btn
          size="12px"
          outline
          icon="folder_open"
          label="Open"
          title="List repository content"
          @click="openRepositoryDialog(repo)"
          data-cy="openRepositoryDialog"
        />
      </q-item-section>

      <q-item-section>
        <q-item-label lines="1">
          <span class="text-weight-medium">{{ repo.name }}</span>
        </q-item-label>
      </q-item-section>

      <q-item-section v-if="repoStore.currentRepo == repo.name" side top>
        <div>
          <q-icon size="24px" name="done"></q-icon>
          Use by default
        </div>
      </q-item-section>
      <q-item-section top side>
        <div class="text-grey-8 q-gutter-xs">
          <q-btn
            size="12px"
            flat
            dense
            round
            icon="archive"
            title="Archive repository"
            @click="archiveRepo(repo)"
            data-cy="archiveRepo"
          />
          <q-btn
            size="12px"
            flat
            dense
            round
            icon="share"
            v-if="repo.owner == true"
            title="Share repository"
            @click="openUsersDialog(repo)"
            data-cy="deleteRepo"
            />
          <q-btn
            size="12px"
            flat
            dense
            round
            icon="delete"
            title="Delete repository"
            v-if="repo.owner == true"
            @click="deleteRepo(repo)"
            data-cy="deleteRepo"
          />
          <q-btn
            v-if="repoStore.currentRepo != repo.name"
            size="12px"
            flat
            dense
            round
            icon="done"
            title="Mark as Default"
            @click="markAsDefault(repo)"
            data-cy="markAsDefault"
          />
        </div>
      </q-item-section>
    </q-item>
  </q-list>

  <q-btn icon="add" outline @click="addRepo" data-cy="addRepo"></q-btn>

  <q-list bordered>
    <q-item-label header>Archived Repositories</q-item-label>

    <q-item
      v-for="repo in repoStore.archivedRepos.values()"
      :key="repo.id"
      data-cy="archivedRepository"
    >
      <q-item-section avatar top>
        <q-icon name="archive" color="black" size="34px" />
      </q-item-section>

      <q-item-section top>
        <q-item-label lines="1">
          <span class="text-weight-medium">{{ repo.name }}</span>
        </q-item-label>
      </q-item-section>

      <q-item-section top side>
        <div class="text-grey-8 q-gutter-xs">
          <q-btn
            class="gt-xs"
            size="12px"
            flat
            dense
            round
            icon="unarchive"
            @click="unarchiveRepo(repo)"
            data-cy="unarchiveRepo"
          />
          <q-btn
            class="gt-xs"
            size="12px"
            flat
            dense
            round
            icon="delete"
            @click="deleteArchivedRepo(repo)"
            data-cy="deleteArchivedRepo"
          />
        </div>
      </q-item-section>
    </q-item>
  </q-list>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { useRepoStore } from 'stores/repoStore';
import { api } from '../../boot/axios';
import { Repository } from '../models';
import RepositoryDialog from './RepositoryDialog.vue';
import RepositoryUsers from './RepositoryUsers.vue';
import { AxiosError, AxiosResponse } from 'axios';

const $q = useQuasar();
const repoStore = useRepoStore();

onMounted(async () => {
  await Promise.all([
    api.get<Repository[]>('/repositories'),
    api.get<Repository[]>('/repositories/archived'),
  ])
    .then((res) => {
      repoStore.repos = new Map<string, Repository>();      
      res[0].data.forEach((repo: Repository) => repoStore.repos.set(repo.id, repo));
      repoStore.archivedRepos = new Map<string, Repository>();
      res[1].data.forEach((repo: Repository) => repoStore.archivedRepos.set(repo.id, repo));
      if (repoStore.repos.size > 0) {
        repoStore.currentRepo = [...repoStore.repos.values()][0].name;
      }
    })
    .catch((error: AxiosError) => {
      $q.notify({ message: error.message, type: 'negative' });
    });
});

const addRepo = () => {
  $q.dialog({
    title: 'Add a new repository',
    message: 'What is the new name of the repository?',
    prompt: {
      model: '',
      isValid: (name) => {
        return name.trim() != '' && !repoStore.repos.has(name.trim());
      },
      type: 'text',
      outlined: true,
    },
    cancel: true,
  }).onOk((repoName) => {
    api
      .post('/repositories/' + repoName)
      .then(() => {
        repoStore.repos.set(repoName, { id: repoName, name: repoName, owner: true });
        if (repoStore.repos.size == 1) {
          repoStore.currentRepo = [...repoStore.repos.values()][0].name;
        }
      })
      .catch((error) => $q.notify({ message: error, type: 'negative' }));
  });
};

const deleteRepo = (repo: Repository) => {
  $q.dialog({
    title: 'Delete a repository',
    message:
      'Are you sure you want to delete the repository: ' +
      repo.name +
      '?',
    cancel: true,
  }).onOk(() => {
    api
      .delete('/repositories/' + repo.id)
      .then(() => {
        repoStore.repos.delete(repo.id);
        if (repoStore.repos.size == 1) {
          repoStore.currentRepo = [...repoStore.repos.values()][0].name;
        }
        if (repoStore.repos.size == 0) {
          repoStore.currentRepo = null;
        }
      })
      .catch((error) => $q.notify({ message: error, type: 'negative' }));
  });
};

const archiveRepo = (repo: Repository) => {
  $q.dialog({
    title: 'Archive a repository',
    message:
      'Are you sure you want to archive the repository: ' +
      repo.name +
      '?',
    cancel: true,
  }).onOk(() => {
    api
      .post('/repositories/archived/' + repo.id)
      .then(() => {
        repoStore.repos.delete(repo.id);
        repoStore.archivedRepos.set(repo.id, repo);
      })
      .catch((error) => $q.notify({ message: error, type: 'negative' }));
  });
};

const deleteArchivedRepo = (repo: Repository) => {
  $q.dialog({
    title: 'Delete an archived repository',
    message:
      'Are you sure you want to delete the archived repository: ' +
      repo.name +
      '?',
    cancel: true,
  }).onOk(() => {
    api
      .delete('/repositories/' + repo.id)
      .then(() => {
        repoStore.archivedRepos.delete(repo.id);
      })
      .catch((error) => $q.notify({ message: error, type: 'negative' }));
  });
};

const unarchiveRepo = (repo: Repository) => {
  $q.dialog({
    title: 'Unarchive an archived repository',
    message:
      'Are you sure you want to unarchive the archived repository: ' +
      repo.name +
      '?',
    cancel: true,
  }).onOk(() => {
    api
      .post('/repositories/archived/' + repo.id)
      .then(() => {
        repoStore.archivedRepos.delete(repo.id);
        repoStore.repos.set(repo.id, repo);
        if (repoStore.repos.size == 1) {
          repoStore.currentRepo = [...repoStore.repos.values()][0].name;
        }
      })
      .catch((error) => $q.notify({ message: error, type: 'negative' }));
  });
};

const markAsDefault = (repo: Repository) => {
  $q.dialog({
    title: 'Confirm',
    message:
      'Are you sure you want to mark the repository: ' +
      repo.name +
      ' as default?',
    cancel: true,
  }).onOk(() => {
    repoStore.currentRepo = repo.id;
  });
};

const openRepositoryDialog = async (repo: Repository) => {
  await api
    .get('/repositories/' + repo.id)
    .then((res: AxiosResponse) => {
      const dataflows: [] = res.data;
      if (dataflows.length == 0) {
        $q.notify({
          message: 'No dataflows available in the repository: ' + repo.name,
          type: 'negative',
        });
      } else {
        $q.dialog({
          component: RepositoryDialog,
          componentProps: { repo, dataflows },
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

const openUsersDialog = async (repo: Repository) => {
  await api
    .get('/repositories/' + repo.id + '/users')
    .then((res: AxiosResponse) => {
      const repoUsers: string[] = res.data;
      $q.dialog({
          component: RepositoryUsers,
          componentProps: { repo, repoUsers },
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
