<template>
<div class="footer">
    <div class="menuBar">
        <div :class="currentMenu == 1 ? 'item active' : 'item'"
            @click="$emit('changeMenu', 1)">
            <span class="item-name"><i class="bi bi-wallet2"></i> 장부</span>
        </div>
        <div :class="currentMenu == 2 ? 'item active' : 'item'"
            @click="$emit('changeMenu', 2)">
            <span class="item-name"><i class="bi bi-tag"></i> 계정과목</span>
        </div>
        <div :class="currentMenu == 3 ? 'item active' : 'item'"
            @click="$emit('changeMenu', 3)">
            <span class="item-name"><i class="bi bi-file-earmark-medical"></i> 공금보고서</span>
        </div>
    </div>

</div>
</template>

<script>
export default {
    props: ['currentMenu']
}
</script>

<style scoped>

.menuBar {
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
}

.menuBar>.item {
    display: inline-flex;
    justify-content: center;

    box-sizing: border-box;
    align-items: center;
    
    width: 100px;
    height: 30px;

    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;


    font-size: 14px;
    font-weight: 600;

    background-color: var(--light-color);

    user-select: none;
    -webkit-user-select: none;
    -ms-user-select: none;
    -webkit-touch-callout: none;

    cursor: pointer;
    transition: all 1s ease;
}

.item-name {
    display: flex;
    align-items: center;
    gap: 5px;
}

.menuBar>.item.active {
    background-color: var(--strong-color);
    color: var(--none-color);
}

.menuBar>.item:hover {
    background-color: var(--strong-color);
    color: var(--none-color);
}


</style>