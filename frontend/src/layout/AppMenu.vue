<script setup>
import { ref } from 'vue';

import AppMenuItem from './AppMenuItem.vue';

const model = ref([
    {
        label: 'Home',
        items: [{ label: 'Dashboard', icon: 'pi pi-fw pi-home', to: '/' }]
    },
    {
        label: 'Crop Health',
        items: [
            { label: 'Table', icon: 'pi pi-fw pi-table', to: '/uikit/table' },
            { label: 'Soil Moisture', icon: 'pi pi-fw pi-chart-bar', to: '/uikit/charts' },
            { label: 'Water Flow', icon: 'pi pi-fw pi-chart-bar', to: '/uikit/water' }
        ]
    },
    {
        label: 'Pages',
        icon: 'pi pi-fw pi-briefcase',
        to: '/pages',
        items: [
            {
                label: 'Inventory Management',
                icon: 'pi pi-fw pi-pencil',
                to: '/pages/crud'
            },
            { label: 'Inventory List', 
              icon: 'pi pi-fw pi-list', 
              to: '/uikit/list' 
            },
        ]
    }
]);
</script>

<template>
    <ul class="layout-menu">
        <template v-for="(item, i) in model">
            <app-menu-item v-if="!item.separator" :key="item.label" :item="item" :index="i"></app-menu-item>
            <li v-if="item.separator" class="menu-separator" :key="'separator-' + i"></li>
        </template>
    </ul>
</template>

<style lang="scss" scoped></style>
