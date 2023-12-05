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

import { VueWrapper } from '@vue/test-utils';
import BoolConfigComponent from '../BoolConfigComponent.vue';
import { SimpleNodeParameter } from '../../models';

describe('BoolConfigComponent', () => {
  it('has an initial value', () => {
    cy.mount(BoolConfigComponent, {
      props: {
        modelValue: true,
        param: {} as SimpleNodeParameter,
        nodeName: 'node',
      },
    });
    cy.dataCy('toggle').then((toggle) => {
      const v = Cypress.vueWrapper as unknown as VueWrapper<
        InstanceType<typeof BoolConfigComponent>
      >;
      expect(v.vm.modelValue).to.be.true;
      cy.wrap(toggle).should('be.checked');
    });
  });

  it('supports null value', () => {
    cy.mount(BoolConfigComponent, {
      props: {
        modelValue: null,
        param: {} as SimpleNodeParameter,
        nodeName: 'node',
      },
    });

    cy.dataCy('toggle').then(() => {
      const v = Cypress.vueWrapper as unknown as VueWrapper<
        InstanceType<typeof BoolConfigComponent>
      >;
      expect(v.vm.modelValue).to.equal(null);
      cy.dataCy('toggle')
        .check()
        .then(() => {
          expect(v.emitted('update:modelValue')[0][0]).to.equal(true);
        });
    });
  });
});
