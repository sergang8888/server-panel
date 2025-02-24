<template>
  <div>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="监控" name="monitor">
        <Monitor />
      </el-tab-pane>
      <el-tab-pane label="文件管理" name="files">
        <FileManager />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import Monitor from './components/Monitor.vue'
import FileManager from './components/FileManager.vue'

export default {
  components: { Monitor, FileManager },
  data() {
    return {
      activeTab: 'monitor'
    }
  }
}
</script>