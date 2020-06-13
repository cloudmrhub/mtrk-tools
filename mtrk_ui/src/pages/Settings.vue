<template>
  <q-page class="flex">
    <div>This will come soon too</div>
  </q-page>
</template>

<script>
export default {
  name: 'Settings',
  created () {
    this.$emit('childinit', 'Settings')
  }
}
</script>
