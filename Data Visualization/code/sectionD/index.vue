<template>
  <div>
    <h2>Section D</h2>
    <h2>Sex ratio for patent developers</h2>
    <svg ref="svg2" style="width: 600px; height: 300px"></svg>
    <div id="tooltip1" class="tooltip1" style="position: absolute; opacity: 0; background-color: white; border: 1px solid black; padding: 5px; pointer-events: none;">
    </div>
    <h2>Patent group scale distribution</h2>
    <svg ref="svg1" style="width: 600px; height: 350px"></svg>
    <div id="tooltip2" class="tooltip2" style="position: absolute; opacity: 0; background-color: white; border: 1px solid black; padding: 5px; pointer-events: none;">
    </div>
    <h2>Table of Patent Classes</h2>
    <!-- 表格将在此处渲染 -->
    <table v-if="tableData.length">
      <thead>
        <tr>
          <th>Patent Class</th>
          <th>Number of patents of this class</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in tableData" :key="index">
          <td>{{ row.cpc_class }}</td>
          <td>{{ row.count_of_cpc_class }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>未找到相关数据</p>
  </div>
</template>

<script src="./script.js"></script>

<style scoped>
table {
  width: 100%;
  border-collapse: separate; /* 改为separate以确保边框分开显示 */
  border-spacing: 0; /* 设置单元格之间的间距为0 */
}
th, td {
  border: 1px solid #ddd; /* 为单元格添加1像素宽的灰色边框 */
  padding: 8px;
  text-align: left;
}
th {
  background-color: #f2f2f2;
}
</style>