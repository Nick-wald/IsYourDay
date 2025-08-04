<script setup>
import InformationForm from '../components/InformationForm.vue';

const token = localStorage.getItem('access_token')
</script>

<template>
  <InformationForm :token="token" />
</template>