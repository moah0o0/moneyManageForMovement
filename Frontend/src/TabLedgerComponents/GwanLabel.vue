<template>
    <template v-if="label">
        <span class="label">
            <div class="plus none-select" v-if="label == '수입'">+</div> 
            <div class="minus none-select" v-if="label == '지출'">-</div>
            {{ label }}
        </span>
    </template>

</template>

<style scoped>

.plus {
    font-weight: 600;
    color: var(--danger-color);

}

.minus {
    font-weight: 600;
    color: var(--primary-color);
}

.none-select {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none; 
  user-select: none;
}


</style>

<script>

export default {
    props: ['label'],
}
</script>
