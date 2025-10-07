<template>
  <BarHeader 
    :login-status="LOGIN_STATUS" 
    :login-info="LOGIN_INFO" 
    :organization-name=ORGANIZATION_NAME
    @update="update_login_data"></BarHeader>
  <BarMenu :current-menu=CURRENT_MENU @change-menu="menuChange"></BarMenu>

  <div class="area-main-content">
  <TabLedger v-if="CURRENT_MENU == 1" 
             :key="LOGIN_STATUS"
             :login-status="LOGIN_STATUS" 
             :init-date=ORGANIZATION_INITDATE
             :canEdit="LOGIN_PERMISSION == 'editor'" ></TabLedger>
             
  <TabAssets v-if="CURRENT_MENU == 2" 
             :key="LOGIN_STATUS"
             :login-status="LOGIN_STATUS" 
             :init-date=ORGANIZATION_INITDATE
            :canEdit="LOGIN_PERMISSION == 'editor'"> </TabAssets>
             
  <TabReport v-if="CURRENT_MENU == 3" 
             :key="LOGIN_STATUS"
             :login-status="LOGIN_STATUS" 
             :init-date=ORGANIZATION_INITDATE 
             :organization-name="ORGANIZATION_NAME"></TabReport>
  </div>
</template>




<script>
import './style.css'

import PocketBase from 'pocketbase';
const pb = new PocketBase(__POCKETBASE_API_BASE_URL__);

import BarHeader from './BarHeader.vue'
import BarMenu from './BarMenu.vue'
import TabLedger from './TabLedger.vue'
import TabAssets from './TabAssets.vue'
import TabReport from './TabReport.vue'

export default {
  components: {
    TabLedger,
    TabAssets,
    TabReport,
    BarHeader,
    BarMenu
  },
  
  data(){
    return {
      ORGANIZATION_NAME: __ORGANIZATION_NAME__,
      ORGANIZATION_INITDATE:  Number(__ORGANIZATION_INIT_DATE__),
      
      LOGIN_INFO: null,
      LOGIN_STATUS: false,
      
      CURRENT_MENU: 1, // 1:장부, 2:계정과목, 3:결산

      unsubscribe:null,

    }
  },

  async created(){
    const params = new URLSearchParams(window.location.search)

    const CURRENT_MENU = params.get("current_menu")

    if(CURRENT_MENU != null){
      this.CURRENT_MENU = parseInt(CURRENT_MENU)
    }

    this.update_login_data()
  },

  async beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },

  methods: {
    update_login_data(){
      this.LOGIN_STATUS = pb.authStore.isValid
      this.LOGIN_INFO = pb.authStore.record
      this.LOGIN_PERMISSION = pb.authStore.record.permission
    },

    menuChange(new_menu){
      this.CURRENT_MENU = new_menu
      const url = new URL(window.location);
      url.searchParams.set('current_menu', new_menu);
      window.history.pushState({}, '', url);
    }
  }
}
</script>


