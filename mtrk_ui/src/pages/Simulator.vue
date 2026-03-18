<template>
  <q-page class="flex">
    <div>Coming in some time...</div>
  </q-page>
</template>

<script>
export default {
  name: 'Simulator',
  created () {
    this.$emit('childinit', 'Simulator')
  }
}
</script>
