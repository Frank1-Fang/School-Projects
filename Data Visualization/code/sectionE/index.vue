<template>
  <div>
    <h2>Chord Diagram</h2>

    <!-- SVG 图表 -->
    <svg ref="svg" :width="width" :height="height"></svg>

    <!-- 动态条目型选择框 -->
    <div class="company-selectors">
      <div
        v-for="(company, index) in selectedCompanies"
        :key="index"
        class="company-selector"
        :class="{ first: index === 0 }"
      >
        <label>
          <!-- 第一个选择框的圆形图标 -->
          <span v-if="index === 0">
            <button 
              class="filter-button" 
              :style="{ backgroundColor: company ? colorScale(company) : '#ffffff' }"
            ></button>
          </span>
          <!-- 筛选按钮 -->
          <span v-if="index > 0">
            <button
              class="filter-button"
              :style="{ backgroundColor: company ? colorScale(company) : '#ffffff' }"
              @click="toggleFilter(index)"
              :title="filterActive[index] ? 'Cancel Filter' : 'Filter'"
            ></button>
          </span>
          Select Company {{ index + 1 }}:
          <select 
            v-model="selectedCompanies[index]" 
            :disabled="index > 0 && !filteredOptions[index].length" 
            class="company-dropdown"
            @change="onCompanyChange(index)"
          >
            <option v-for="option in filteredOptions[index]" :key="option" :value="option">
              {{ option }}
            </option>
          </select>
          <!-- 删除按钮 -->
          <button v-if="index > 0" class="clear-button" @click="removeSelector(index)" title="delete">×</button>
        </label>
      </div>

      <!-- 添加新公司按钮 -->
      <button @click="addCompany">Add Another Company</button>
    </div >
    <div id="line-chart" style="width: 100%; height: 400px;"></div>
    <!-- 动态生成表格，显示人员信息 -->
    <div v-if="inventorTableData.length > 0" class="inventor-table">
      <h3>Inventor Information</h3>
      <table>
        <tbody>
          <tr v-for="(id, index) in firstColumn" :key="index">
            <td
              v-bind:class="{ hover: hoveredId === id }" 
              v-bind:title="getInventorInfo(id)"
            >
              {{ id }}
            </td>
            <td
              v-bind:class="{ hover: hoveredId === secondColumn[index] }" 
              v-bind:title="getInventorInfo(secondColumn[index])"
            >
              {{ secondColumn[index] || '' }}
            </td>
            <td
              v-bind:class="{ hover: hoveredId === thirdColumn[index] }" 
              v-bind:title="getInventorInfo(thirdColumn[index])"
            >
              {{ thirdColumn[index] || '' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
 
    
  </div>
</template>


<script src="./script.js"></script>

<style scoped>
.company-selectors {
  margin-top: 20px;
  margin-bottom: 40px;
  max-height: 300px; /* 设置最大高度，根据需要调整 */
  overflow-y: auto; /* 启用垂直滚动条 */
  border: 2px solid #ccc; /* 添加边框 */
  border-radius: 8px; /* 可选，添加圆角 */
  padding: 10px; /* 可选，添加内边距 */
  width: 500px; /* 设置固定宽度，可以根据需要调整 */
  margin-left: 85px; /* 向右平移 20px，调整此值以获得所需的效果 */
}
.company-selector {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  border: 1px solid #ddd; /* 给每个选择框添加边框 */
  border-radius: 4px; /* 可选，添加圆角 */
  padding: 5px; /* 可选，添加内边距 */
}
.company-selector.first {
  margin-left: 0px; /* 第一个选择框向右偏移 */
}
.company-dropdown {
  width: 250px;
  height:30px
}
.filter-button {
  width: 24px;
  height: 24px;
  opacity:0.7;
  border-radius: 50%;
  border: 1px solid #ccc;
  cursor: pointer;
  margin-right: 10px;
  position: relative;
}
.filter-button:hover{
  opacity:1;
}
/* 当 filterActive[index] 为 true 时，圆形中心出现一个小点 */
.filter-button::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #000000;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.2s;
}

/* 如果 filterActive[index] 为 true, 显示圆心的小点 */
.filter-button.active::after {
  opacity: 1;
}
.filter-button::hover {
  background-color: #f0f0f0;
}
.clear-button {
  margin-left: 10px;
  cursor: pointer;
  border: none;
  position:relative;
  background: transparent;
  font-size: 16px;
  color: #333;
}
.clear-button:hover {
  outline: none; /* 防止浏览器默认的悬停效果 */
}

/* 悬停时添加方框效果 */
.clear-button:hover::before {
  content: "";
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  border: 1px solid #999; /* 方框颜色 */
  border-radius: 4px; /* 可选：让方框有圆角效果 */
  pointer-events: none; /* 禁止鼠标事件，避免干扰按钮点击 */
}
.center-dot {
  fill: #000000;  /* 中心的点的颜色 */
}
.inventor-table {
  margin-left: 85px; /* 向右平移30px */
  margin-top: 20px;
  width:500px;
  max-height: 300px; /* 设置最大高度，根据需要调整 */
  overflow-y: auto; /* 启用垂直滚动条 */
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 10px;
  background-color: #f9f9f9;
}

.inventor-table table {
  width: 100%;
  border-collapse: collapse;
}

.inventor-table th,
.inventor-table td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}
.inventor-table tr:hover {
  background-color: #f1f1f1;
}    
</style>