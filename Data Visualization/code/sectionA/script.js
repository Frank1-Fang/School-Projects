import * as d3 from 'd3';
import { EventBus } from '../eventbus';

export default {
    data() {
        return {
            width: 800, // SVG 宽度
            height: 400, // SVG 高度
            margin: { top: 20, right: 30, bottom: 70, left: 80 }, // 图表边距
            debounceTimeout: null, // 在 data 中定义 debounceTimeout
        };
    },
    async mounted() {
        try {
            // 加载 CSV 数据
            const response = await fetch('../../../static/patent_yearly_counts.csv');
            const csvText = await response.text();

            // 解析 CSV 数据
            const data = d3.csvParse(csvText, d3.autoType); // 自动解析数字列

            // 绘制折线图
            this.drawLineChart(data);
        } catch (error) {
            console.error('Error loading CSV data:', error);
        }
    },
    methods: {
        drawLineChart(data) {
            const { width, height, margin } = this;

            // 创建 SVG 容器
            const svg = d3
                .select(this.$refs.svg)
                .attr('viewBox', `0 0 ${width} ${height}`)
                .append('g')
                .attr('transform', `translate(${margin.left},${margin.top})`);

            const chartWidth = width - margin.left - margin.right;
            const chartHeight = height - margin.top - margin.bottom;

            // 设置 X 轴比例尺
            const xScale = d3
                .scaleLinear()
                .domain(d3.extent(data, (d) => d[data.columns[0]])) // 使用第一列（年份）作为横轴
                .range([0, chartWidth]);

            // 设置 Y 轴比例尺
            const yScale = d3
                .scaleLinear()
                .domain([0, d3.max(data, (d) => d[data.columns[1]])]) // 使用第二列（专利数）作为纵轴
                .range([chartHeight, 0]);

            // 绘制 X 轴
            const xAxis = d3.axisBottom(xScale).ticks(data.length).tickFormat(d3.format('d'));
            svg
                .append('g')
                .attr('transform', `translate(0,${chartHeight})`)
                .call(xAxis)
                .selectAll('text') // 倾斜处理 X 轴文本
                .style('text-anchor', 'end')
                .attr('transform', 'rotate(-45)')
                .attr('dx', '-0.5em')
                .attr('dy', '0.5em');

            // 为 X 轴添加单位
            svg
                .append('text')
                .attr('x', chartWidth / 2)
                .attr('y', height - margin.bottom + 40)
                .attr('text-anchor', 'middle')
                .attr('font-size', '12px')
                .text('Year');

            // 绘制 Y 轴
            const yAxis = d3.axisLeft(yScale);
            svg.append('g').call(yAxis);

            // 为 Y 轴添加单位
            svg
                .append('text')
                .attr('transform', 'rotate(-90)')
                .attr('x', -chartHeight / 2)
                .attr('y', -margin.left + 20)
                .attr('text-anchor', 'middle')
                .attr('font-size', '12px')
                .text('Number of patents');

            // 绘制折线
            const line = d3
                .line()
                .x((d) => xScale(d[data.columns[0]])) // 第一列作为 X 值
                .y((d) => yScale(d[data.columns[1]])); // 第二列作为 Y 值

            svg
                .append('path')
                .datum(data)
                .attr('fill', 'none')
                .attr('stroke', 'SlateGrey') // 折线颜色
                .attr('stroke-width', 2)
                .attr('d', line);

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

            // 绘制节点
            svg
                .selectAll('.node')
                .data(data)
                .join('circle')
                .attr('class', 'node')
                .attr('cx', (d) => xScale(d[data.columns[0]]))
                .attr('cy', (d) => yScale(d[data.columns[1]]))
                .attr('r', 4)
                .attr('fill', '#CD3333') // 节点颜色

                .on('mouseover', function (event, d) {
                    // 高亮当前节点
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('r', 8)
                        .attr('fill', 'orange');

                    // 显示 Tooltip
                    tooltip
                        .style('display', 'block')
                        .html(`Year: ${d[data.columns[0]]}<br># of patents: ${d[data.columns[1]]}`)
                        .style('left', `${event.pageX + 10}px`)
                        .style('top', `${event.pageY + 10}px`);
                })
                .on('mouseout', function () {
                    // 恢复节点样式
                    d3.select(this)
                        .transition()
                        .duration(200)
                        .attr('r', 4)
                        .attr('fill', '#CD3333');

                    // 隐藏 Tooltip
                    tooltip.style('display', 'none');
                });
            // 添加刷选功能
            this.addBrush(svg, xScale, yScale, data, line);
        },
        addBrush(svg, xScale, yScale, data, line, debounceTimeout) {
            const { width, height, margin } = this;

            // 创建刷选工具
            const brush = d3
                .brushX()
                .extent([
                    [0, height - margin.bottom - 30],
                    [width - margin.right - margin.left, height - margin.bottom - 10],
                ])
                .on('brush end', (event) => {
                    const selection = event.selection;
                    if (!selection) return;

                    // 获取刷选范围
                    const [x0, x1] = selection.map(xScale.invert);

                    //EventBus.emit('time-range-selected', { start: Math.floor(x0) + 1, end: Math.ceil(x1) - 1 });
                    //console.log('A 区域发送事件:', { start: Math.floor(x0), end: Math.ceil(x1) });

                    // 添加防抖逻辑，限制事件触发频率
                    if (debounceTimeout) clearTimeout(debounceTimeout);

                    debounceTimeout = setTimeout(() => {
                        EventBus.emit('time-range-selected', { start: Math.floor(x0) + 1, end: Math.ceil(x1) - 1 });
                        console.log('A 区域发送事件（防抖触发）:', { start: Math.floor(x0), end: Math.ceil(x1) });
                    }, 3000); // 设置防抖延迟时间（单位：毫秒）

                    // 筛选刷选范围内的数据
                    const brushedData = data.filter(
                        (d) => d[data.columns[0]] >= x0 && d[data.columns[0]] <= x1
                    );

                    // 更新折线高亮和虚化
                    this.updateHighlight(svg, data, brushedData, line);

                });

            // 添加刷选区域
            svg.append('g').attr('class', 'brush').call(brush);
        },

        updateHighlight(svg, data, brushedData, line) {
            // 虚化所有折线
            //svg.select('.line')
            //.datum(data)
            //.attr('stroke', 'lightgray') // 虚化其余折线
            //.attr('stroke-width', 1);

            // 高亮刷选范围内的折线
            svg.selectAll('.highlight').remove(); // 清除旧高亮
            svg
                .append('path')
                .datum(brushedData)
                .attr('class', 'highlight')
                .attr('fill', 'none')
                .attr('stroke', '#FFD700') // 高亮颜色
                .attr('stroke-width', 2)
                .attr('d', line);


        },
    },
};
