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
  <q-layout view="hHh LpR fFf">
    <q-header elevated bordered>
      <q-toolbar>
        <q-toolbar-title>Rainfall</q-toolbar-title>
      </q-toolbar>
    </q-header>
    <q-space></q-space>
    <div class="row" style="height: 90vh">
      <div class="q-pa-xl col-0 col-md-6 flex justify-center content-center">
        <img src="~assets/unicam-logo.png" class="q-ma-xl responsive" alt="login-image">
      </div>
      <div v-bind:class="{ 'justify-center': $q.screen.md || $q.screen.sm || $q.screen.xs }"
        class="col-12 col-md-6 flex content-center">
        <q-card v-bind:style="$q.screen.lt.sm ? { 'width': '80%' } : { 'width': '50%' }">
          <q-card-section>
            <q-form class="q-gutter-md" @submit.prevent="onSubmit">
              <q-input filled v-model="username" label="Username" lazy-rules
                :rules="[val => val && val.length > 0 || 'Mandatory field']" />

              <q-input filled v-model="password" label="Password" lazy-rules
                :rules="[val => val && val.length > 0 || 'Mandatory field']" :type="isPwd ? 'password' : 'text'">

                <template v-slot:append>
                  <q-icon :name="isPwd ? 'visibility_off' : 'visibility'" class="cursor-pointer"
                    @click="isPwd = !isPwd" />
                </template>
              </q-input>
              <div>
                <q-btn class="full-width" color="primary" label="Login" type="submit" rounded></q-btn>
              </div>
              <div>
                <q-btn class="full-width" color="grey" label="Login as guest" @click="onGuestLogin()" rounded></q-btn>
              </div>
            </q-form>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-layout>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { api } from '../boot/axios';
import { useUserStore } from 'src/stores/userStore';
import { ref } from 'vue'
import { useQuasar } from 'quasar';

const $q = useQuasar()
const router = useRouter();
const userStore = useUserStore()
let username = ref("")
let password = ref("")
let isPwd = ref(true)

let onSubmit = async () => {
  userStore.doLogin({
    'username': username.value,
    'password': password.value,
  }).then(() => {
    router.push({ name: 'canvas' })
  }).catch((error) => {
    username.value = ""
    password.value = ""
    $q.notify({
      type: 'negative',
      message: 'Wrong credentials!'
    })
  })
}

let onGuestLogin = async () => {
  userStore.doLogin({
    'username': 'guest',
    'password': 'guest',
  }).then(() => {
    router.push({ name: 'canvas' })
  }).catch((error) => {
    username.value = ""
    password.value = ""
    $q.notify({
      type: 'negative',
      message: 'Wrong credentials!'
    })
  })
}

</script>
