<template>
  <q-page class="flex">
    <div style="margin-top: 32px;" >Hello!</div>

          <q-page-sticky expand position="top">
           <q-toolbar class="bg-grey-3" style="color: #000; min-height: 32px; border-bottom: 1px solid rgba(0, 0, 0, 0.12);">
            <div class="q-pl-sm row">
              <div class="cursor-pointer non-selectable mainmenu">
                File
                <q-menu>
                  <q-list dense style="min-width: 100px">
                    <q-item clickable v-close-popup>
                      <q-item-section>Open...</q-item-section>
                    </q-item>
                    <q-item clickable v-close-popup>
                      <q-item-section>New</q-item-section>
                    </q-item>

                    <q-separator />

                    <q-item clickable>
                      <q-item-section>Preferences</q-item-section>
                      <q-item-section side>
                        <q-icon name="keyboard_arrow_right" />
                      </q-item-section>

                      <q-menu anchor="top right" self="top left">
                        <q-list>
                          <q-item
                            v-for="n in 3"
                            :key="n"
                            dense
                            clickable
                          >
                            <q-item-section>Submenu Label</q-item-section>
                            <q-item-section side>
                              <q-icon name="keyboard_arrow_right" />
                            </q-item-section>
                            <q-menu auto-close anchor="top right" self="top left">
                              <q-list>
                                <q-item
                                  v-for="n in 3"
                                  :key="n"
                                  dense
                                  clickable
                                >
                                  <q-item-section>3rd level Label</q-item-section>
                                </q-item>
                              </q-list>
                            </q-menu>
                          </q-item>
                        </q-list>
                      </q-menu>
                    </q-item>

                    <q-separator />

                    <q-item clickable v-close-popup>
                      <q-item-section>Quit</q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </div>

              <div class="q-ml-md cursor-pointer non-selectable mainmenu">
                Edit
                <q-menu auto-close>
                  <q-list dense style="min-width: 100px">
                    <q-item clickable>
                      <q-item-section>Cut</q-item-section>
                    </q-item>
                    <q-item clickable>
                      <q-item-section>Copy</q-item-section>
                    </q-item>
                    <q-item clickable>
                      <q-item-section>Paste</q-item-section>
                    </q-item>
                    <q-separator />
                    <q-item clickable>
                      <q-item-section>Select All</q-item-section>
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
  name: 'Generator',
  data () {
    return {
      pageName: 'Generator'
    }
  },
  created () {
    this.$emit('childinit', 'Generator')
  }
}
</script>
