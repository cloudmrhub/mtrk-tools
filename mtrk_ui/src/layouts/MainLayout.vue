<template>
    <q-layout>
      <q-header class="bg-dark">
        <q-toolbar>
          <q-img
          src="~assets/mtrk_top.png"
          spinner-color="white"
          style="margin-left: 4px; max-width: 100px; min-width: 100px;"
          />
          <q-toolbar-title expand class="q-ml-sm" style="border-left: 1px solid #FFF;">{{ name }}</q-toolbar-title>
          <q-btn flat @click="drawer = !drawer" dense icon="apps" />
        </q-toolbar>
      </q-header>

      <q-drawer
        side="right"
        v-model="drawer"
        :width="200"
        :breakpoint="500"
        overlay
        bordered
        content-class="bg-grey-3"
      >
        <q-scroll-area class="fit">
          <q-list v-for="(menuItem, index) in menuList" :key="index">

            <q-item clickable :active="menuItem.target === $route.path" :to="menuItem.target"  v-ripple>
              <q-item-section avatar>
                <q-icon :name="menuItem.icon" />
              </q-item-section>
              <q-item-section>
                {{ menuItem.label }}
              </q-item-section>
            </q-item>

            <q-separator v-if="menuItem.separator" />

          </q-list>
            <q-item clickable v-ripple @click.native="onHelpClick()">
              <q-item-section avatar>
                <q-icon name="help" />
              </q-item-section>
              <q-item-section>
                Help
              </q-item-section>
            </q-item>

        </q-scroll-area>
      </q-drawer>

      <q-page-container>
        <q-page padding>
          <router-view v-on:childinit="onChildInit" />
        </q-page>
      </q-page-container>
    </q-layout>
</template>

<script>
import { openURL } from 'quasar'

const menuList = [
  {
    icon: 'fas fa-binoculars',
    label: 'Inspector',
    separator: false,
    target: '/inspector'
  },
  {
    icon: 'fas fa-mortar-pestle',
    label: 'Generator',
    separator: false,
    target: '/generator'
  },
  {
    icon: 'fas fa-vial',
    label: 'Simulator',
    separator: true,
    target: '/simulator'
  },
  {
    icon: 'settings',
    label: 'Settings',
    separator: false,
    target: '/settings'
  }
]

export default {
  data () {
    return {
      drawer: false,
      menuList,
      name
    }
  },
  methods: {
    onChildInit (value) {
      this.name = value
      document.title = 'mtrk | ' + value
    },
    onHelpClick: function () {
      openURL('https://mtrk-dev.github.io')
    }
  }
}
</script>
