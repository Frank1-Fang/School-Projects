import * as d3 from 'd3';
import { EventBus } from '../eventbus';

export default {
    data() {
        return {
            width: 600, // SVG 宽度
            height: 400, // SVG 高度
            margin: { top: 20, right: 30, bottom: 50, left: 50 }, // 图表边距
        };
    },
    async mounted() {
        // 加载 PCA 聚类数据
        try {
            const data = await d3.csv('../../../static/pca_clustered_data.csv', d3.autoType); // 自动解析数字
            this.drawScatterPlot(data); // 调用绘制方法
        } catch (error) {
            console.error('Error loading data:', error);
        }
    },
    methods: {
        drawScatterPlot(data) {
            const { width, height, margin } = this;

            // 手动定义 X 和 Y 轴的取值范围
            const xDomain = [0, 80]; // X 轴范围，从 0 到 300
            const yDomain = [-10, 20]; // Y 轴范围，从 -10 到 70

            // 创建 SVG 容器
            const svg = d3
                .select(this.$refs.scatterContainer)
                .append('svg')
                .attr('width', width)
                .attr('height', height);

            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;

            // 创建图表组
            const chart = svg
                .append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);

            // 定义比例尺，设置手动范围
            const xScale = d3.scaleLinear().domain(xDomain).range([0, chartWidth]);
            const yScale = d3.scaleLinear().domain(yDomain).range([chartHeight, 0]);

            // 定义颜色比例尺
            const colorScale = d3.scaleOrdinal(d3.schemeCategory10); // 根据 cluster 映射颜色

            // 绘制 X 轴
            const xAxis = d3.axisBottom(xScale);

            chart
                .append('g')
                .attr('transform', `translate(0,${chartHeight})`)
                .call(xAxis);

            // 添加 X 轴标签
            chart
                .append('text')
                .attr('x', chartWidth / 2)
                .attr('y', chartHeight + 40)
                .attr('text-anchor', 'middle')
                .attr('font-size', '14px')
                .text('PCA Component 1');

            // 绘制 Y 轴
            const yAxis = d3.axisLeft(yScale);

            chart.append('g').call(yAxis);

            // 添加 Y 轴标签
            chart
                .append('text')
                .attr('transform', 'rotate(-90)')
                .attr('x', -chartHeight / 2)
                .attr('y', -40)
                .attr('text-anchor', 'middle')
                .attr('font-size', '14px')
                .text('PCA Component 2');



            // 创建全局 Tooltip，只创建一次
            const tooltip = d3
                .select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('position', 'absolute')
                .style('background', '#fff')
                .style('border', '1px solid #ccc')
                .style('padding', '5px')
                .style('pointer-events', 'none')
                .style('font-size', '12px')
                .style('display', 'none');

            // 绘制散点
            const circles = chart
                .selectAll('circle')
                .data(data)
                .join('circle')
                .attr('cx', (d) => xScale(d.pca1)) // 使用 X 比例尺
                .attr('cy', (d) => yScale(d.pca2)) // 使用 Y 比例尺

                .attr('r', 2) // 点的大小
                .attr('fill', (d) => colorScale(d.cluster)) // 按 cluster 着色
                .on('mouseover', function (event, d) {
                    // 鼠标悬浮事件
                    d3.select(this)
                        .transition()
                        .duration(100)
                        .attr('r', 4); // 放大点

                    tooltip
                        .style('display', 'block') // 显示 Tooltip
                        .html(
                            `Organization: ${d.original_organization}<br>Cluster: ${d.cluster}`
                        )
                        .style('left', `${event.pageX + 10}px`)
                        .style('top', `${event.pageY + 10}px`);
                })
                .on('mouseout', function () {
                    // 鼠标离开事件
                    d3.select(this)
                        .transition()
                        .duration(100)
                        .attr('r', 2); // 恢复原大小

                    tooltip.style('display', 'none'); // 隐藏 Tooltip
                });
            
            EventBus.on('institution-selected', (selectedInstitution) => {
                // 获取选中机构的 cluster
                const selectedData = data.find((d) => d.original_organization === selectedInstitution);

                if (!selectedData) return;

                const selectedCluster = selectedData.cluster;

                // 高亮同一类的所有点
                circles.attr('fill', (d) =>
                    d.cluster === selectedCluster ? colorScale(d.cluster) : '#ccc'
                );

                // 改变选中点的颜色
                circles
                    .filter((d) => d.original_organization === selectedInstitution)
                    .attr('fill', 'red')
                    .attr('r', 6); // 增大选中点的半径

                console.log(`Selected institution: ${selectedInstitution}`);
            });
        },
    },
};
