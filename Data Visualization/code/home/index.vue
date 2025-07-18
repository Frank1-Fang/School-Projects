<template>
  <div class="grid-container">
    <A class="a-container" />
    <B class="b-container" />
    <C class="c-container" />
    <D class="d-container" />
    <E class="e-container" />
  </div>
</template>

<script src="./script.js"></script>

<style lang="less">
body {
  margin: 0;
  padding: 0;
  background-color: #f5f5f5; /* 设置淡灰色 */
}

.grid-container {
  display: grid;
  grid-template-columns: 810px 720px 720px; /* 定义三列宽度 */
  grid-template-rows: auto; /* 行高自适应内容 */
  gap: 10px; /* 设置网格间距 */
  width: 100%;
  height: 100%;
}

/* 第一列样式 */
.a-container {
  grid-column: 1;
  grid-row: 1;
  height: 450px; /* 第一方框高度 */
  border: 2px solid #a0a0a0;
  border-radius: 8px;
}

.b-container {
  grid-column: 1;
  grid-row: 2;
  height: 450px; /* 第二方框高度 */
  border: 2px solid #a0a0a0;
  border-radius: 8px;
}

.c-container {
  grid-column: 1;
  grid-row: 3;
  height: 1050px; /* 第三方框高度 */
  border: 2px solid #a0a0a0;
  border-radius: 8px;
}

/* 第二列样式 */
.d-container {
  grid-column: 2;
  grid-row: 1 / span 3; /* 第二列跨三行 */
  border: 2px solid #a0a0a0;
  border-radius: 8px;
}

/* 第三列样式 */
.e-container {
  grid-column: 3;
  grid-row: 1 / span 3; /* 第三列跨三行 */
  border: 2px solid #a0a0a0;
  border-radius: 8px;
}
</style>
