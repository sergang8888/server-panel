<template>
  <div>
    <h3>文件管理</h3>
    <el-upload action="http://localhost:8080/api/files/upload" :on-success="fetchFiles">
      <el-button type="primary">上传文件</el-button>
    </el-upload>
    <el-table :data="files" style="margin-top: 20px;">
      <el-table-column prop="name" label="文件名"></el-table-column>
      <el-table-column prop="size" label="大小 (字节)"></el-table-column>
      <el-table-column prop="isDir" label="类型" :formatter="row => row.isDir ? '目录' : '文件'"></el-table-column>
    </el-table>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      files: []
    }
  },
  mounted() {
    this.fetchFiles()
  },
  methods: {
    async fetchFiles() {
      const res = await axios.get('http://localhost:8080/api/files')
      this.files = res.data.files
    }
  }
}
</script>