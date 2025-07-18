<template>
  <div>
    <h2>Section C</h2>
    <!-- 搜索框及选择器 -->
    <div style="display: flex; align-items: center; gap: 20px;">
      <!-- 搜索框 -->
      <div style="position: relative; width: 300px;">
        <input
          type="text"
          placeholder="Please enter the name of institution..."
          v-model="searchQuery"
          @input="updateSuggestions"
          @keydown.enter="handleSearch"
          style="width: 100%; padding: 5px;"
        />
        <!-- 显示建议列表 -->
        <ul
          v-if="suggestions.length > 0"
          style="
            position: absolute;
            top: 35px;
            left: 0;
            width: 100%;
            max-height: 150px;
            overflow-y: auto;
            border: 1px solid #ccc;
            background: white;
            list-style: none;
            padding: 0;
            margin: 0;
            z-index: 1000;"
        >
          <li
            v-for="suggestion in suggestions"
            :key="suggestion"
            @click="selectSuggestion(suggestion)"
            style="
              padding: 5px;
              cursor: pointer;
            "
            @mouseover="hoveredSuggestion = suggestion"
            :style="{
              background: hoveredSuggestion === suggestion ? '#f0f0f0' : 'white',
            }"
          >
            {{ suggestion }}
          </li>
        </ul>
      </div>

      <!-- 细分领域选择器 -->
      <select v-model="selectedField" @change="updateBarChart" style="padding: 5px;">
        <option value="" disabled>Detailed field</option>
        <option v-for="field in availableFields" :key="field" :value="field">
          {{ field }}
        </option>
      </select>

      <!-- 数据类型选择器 -->
      <select v-model="selectedMetric" @change="updateBarChart" style="padding: 5px;">
        <option value="citation">Number of citations</option>
        <option value="patent">Number of patents</option>
      </select>
    </div>

    <!-- 图例 -->
    <div style="display: flex; align-items: center; gap: 10px; margin-left: auto;">
      <!-- 专利图例 -->
      <div style="display: flex; align-items: center; gap: 5px;">
        <div style="width: 15px; height: 15px; background-color: #8B658B; border-radius: 50%;"></div>
        <span style="font-size: 14px;">Citations</span>
      </div>
      <!-- 引用图例 -->
      <div style="display: flex; align-items: center; gap: 5px;">
        <div style="width: 15px; height: 15px; background-color: #EEB422; border-radius: 50%;"></div>
        <span style="font-size: 14px;">Patents</span>
      </div>
    </div>

    <!-- 滚动容器 -->
    <div ref="svgContainer"></div>
  </div>
</template>

<script src="./script.js"></script>

<style scoped>
input {
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}
select {
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}
</style>
