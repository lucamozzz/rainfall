/*
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
 */

import { defineStore } from 'pinia';
import { api } from 'boot/axios'


export const useUserStore = defineStore('userStore', {
    state: () => ({
        me: new String(),
        token: new String(),
        isAuthenticated: false
    }),
    actions: {
        async doLogin(payload: { username: string, password: string }) {
            await api
                .post('/auth/login', new URLSearchParams(payload))
                .then((response) => {
                    const token = response.data.access_token
                    this.$state.token = token
                    api.defaults.headers.common.Authorization = 'Bearer ' + this.$state.token
                    this.getMe()
                }).catch()
        },
        async getMe() {
            await api.get('/auth/me').then((response) => {
                const user = response.data
                this.$state.me = user
                this.$state.isAuthenticated = true
            })
        },
        signOut() {
            api.defaults.headers.common.Authorization = ''
            this.$reset()
        }
    },
    getters: {
        getUser: (state) => () => {
            return state.me
        },
        getToken: (state) => () => {
            return state.token
        },
        getAuthenticated: (state) => () => {
            return state.isAuthenticated
        },
    },
});