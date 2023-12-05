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

import { installQuasar } from '@quasar/quasar-app-extension-testing-unit-vitest';
import { useCanvasStore } from 'src/stores/canvasStore';
import { describe, expect, it } from 'vitest';

installQuasar();

describe('canvasStore test', () => {
  it('has no element at the beginning', async () => {
    const canvasStore = useCanvasStore();
    expect(canvasStore.canvasNodes.size).toBe(0);
    expect(canvasStore.canvasEdges.size).toBe(0);
  });

  it('has methods to clear nodes and edges', async () => {
    const canvasStore = useCanvasStore();
    canvasStore.canvasNodes.set('n1', null);
    canvasStore.canvasNodes.set('n2', null);
    expect(canvasStore.canvasNodes.size).toBe(2);
    canvasStore.canvasEdges.set('e1', null);
    expect(canvasStore.canvasEdges.size).toBe(1);
    canvasStore.clearCanvasNodes();
    expect(canvasStore.canvasNodes.size).toBe(0);
    canvasStore.clearCanvasEdges();
    expect(canvasStore.canvasEdges.size).toBe(0);
  });
});
