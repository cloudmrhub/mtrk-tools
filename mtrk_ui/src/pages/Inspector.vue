<template>
  <q-page class="flex">

          <q-page-sticky expand position="top">
           <q-toolbar class="bg-grey-3" style="color: #000; min-height: 32px; border-bottom: 1px solid rgba(0, 0, 0, 0.12);">
            <div class="q-pl-sm row">
              <div class="cursor-pointer non-selectable mainmenu">
                File
                <q-menu>
                  <q-list dense style="min-width: 100px">
                    <q-item clickable v-close-popup>
                      <q-item-section v-on:click='openSequence()'>Open...</q-item-section>
                    </q-item>
                    <q-item clickable v-close-popup>
                      <q-item-section>Export...</q-item-section>
                    </q-item>

                  </q-list>
                </q-menu>
              </div>

            </div>
          </q-toolbar>
          </q-page-sticky>

  </q-page>
</template>

<script>
export default {
  name: 'Inspector',
  data () {
    return {
      editor: 'What you see is <b>what</b> you get.'
    }
  },
  created () {
    this.$emit('childinit', 'Inspector')
  },
  methods: {
    openSequence () {
      console.log('I have been clicked')
    }
  }
}
</script>
