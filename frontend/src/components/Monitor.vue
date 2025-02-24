<template>
  <div>
    <h3>主机监控</h3>
    <el-row :gutter="20">
      <el-col :span="12">
        <div ref="cpuChart" style="height: 300px;"></div>
      </el-col>
      <el-col :span="12">
        <p>内存: {{ memory.used }} / {{ memory.total }} MB (空闲: {{ memory.free }} MB)</p>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import axios from 'axios'

export default {
  data() {
    return {
      cpu: 0,
      memory: { total: 0, used: 0, free: 0 }
    }
  },
  mounted() {
    this.initChart()
    this.fetchData()
    setInterval(this.fetchData, 5000) // 每5秒刷新
  },
  methods: {
    initChart() {
      const chart = echarts.init(this.$refs.cpuChart)
      chart.setOption({
        title: { text: 'CPU使用率' },
        xAxis: { type: 'category', data: [] },
        yAxis: { type: 'value', max: 100 },
        series: [{ data: [], type: 'line' }]
      })
      this.chart = chart
    },
    async fetchData() {
      const cpuRes = await axios.get('http://localhost:8080/api/monitor/cpu')
      const memRes = await axios.get('http://localhost:8080/api/monitor/memory')
      this.cpu = parseFloat(cpuRes.data.cpu_usage)
      this.memory = memRes.data

      const now = new Date().toLocaleTimeString()
      this.chart.setOption({
        xAxis: { data: [...this.chart.getOption().xAxis[0].data.slice(-9), now] },
        series: [{ data: [...this.chart.getOption().series[0].data.slice(-9), this.cpu] }]
      })
    }
  }
}
</script>