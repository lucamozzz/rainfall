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
  <q-toggle
    dense
    :label="param.name"
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    :toggle-indeterminate="!param.is_mandatory"
    data-cy="toggle"
  ></q-toggle>
</template>

<script setup lang="ts">
import { SimpleNodeParameter } from '../models';

defineProps<{
  modelValue: boolean | null;
  param: SimpleNodeParameter;
  nodeName: string;
}>();
</script>
