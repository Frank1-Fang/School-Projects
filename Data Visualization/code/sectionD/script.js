import * as d3 from 'd3';
import { EventBus } from '../eventbus';

export default {
    data() {
        return {
            // 存储原始数据
            rawRatioData: [],
            // 存储过滤后的数据
            filteredRatioData: [],
            // 选中的公司
            selectedCompany: '',
            // 选中的时间段
            selectedTimeRange: {
                start: Number(),
                end: Number()
            },
            dataset: [],
            companyData: [],
            tableData: [],
            chartConfig1: {
                width: 500,
                height: 300,
                radius: 120,
                color: d3.scaleOrdinal(d3.schemeCategory10)
            },
            chartConfig2: {
                width: 500,
                height: 300,
                radius: 120,
                colors: ['#0066ff', '#ff3399']
            }
        };
    },
    mounted() {
        // 监听公司选择的变化
        EventBus.on('institution-selected', this.handleCompanySelected);
        EventBus.on('time-range-selected', this.handleTimeRangeSelected);

        // 加载CSV数据 (假设你已经有某种方式加载CSV数据)
        d3.csv('../../../static/group_inspection_final.csv').then((data) => {
            this.dataset = data;
            this.updateChart();
        });
        d3.csv('../../../static/sex_ratio_data_updated.csv').then(ratioData => {
            this.rawRatioData = ratioData;
            // 初始化图表
            this.renderRatioChart();
        });
        d3.csv('../../../static/class_distribution_updated.csv').then((classData) => {
            this.rawClassData = classData;
            this.updateClassTableData();
        });
    },
    beforeUnmount() {
        EventBus.off('institution-selected', this.handleCompanySelected);
        EventBus.off('time-range-selected', this.handleTimeRangeSelected);
    },
    methods: {
        handleCompanySelected(company) {
            this.selectedCompany = company;
            // 过滤数据并重新渲染图表
            this.filterDataAndRenderChart();
            this.filterData();
            this.updateChart();
            this.updateClassTableData();
        },
        // 处理时间段选择事件
        handleTimeRangeSelected(timeRange) {
            this.selectedTimeRange = timeRange;
            // 过滤数据并重新渲染图表
            this.filterDataAndRenderChart();
        },
        filterData() {
            const { dataset, selectedCompany } = this;

            this.companyData = dataset.filter(d => {
                return d.original_organization === selectedCompany;
            });
        },
        updateChart() {
            const { companyData } = this;

            let string = '';
            companyData.forEach(function (row) {
                string = row.group_division;
            });
            const groupString = string;

            const divisions = groupString.slice(1, -1).split(', ');

            const groupDivisions = divisions.map(Number);

            const distribution = [0, 0, 0]; // (0, 3], [4, 6], [7, +∞)

            groupDivisions.forEach((num) => {
                if (num > 0 && num <= 3) {
                    distribution[0]++;
                } else if (num > 3 && num <= 6) {
                    distribution[1]++;
                } else if (num >= 7) {
                    distribution[2]++;
                }
            });

            this.createDonutChart(distribution);
        },
        createDonutChart(data) {
            const { chartConfig1 } = this;
            console.log(data);
            const total = data.reduce((sum, value) => sum + value, 0);

            // 转换数据为适合d3.js的格式
            const dataForChart = data.map((value, index) => ({
                label: `${index * 3 + 1} and more persons`,
                value: value,
                percentage: (value / total) * 100
            }));
            console.log(dataForChart);
            // 设置SVG的宽度和高度
            const { width, height, radius, color } = chartConfig1;


            // 创建SVG容器
            const svg1 = d3.select(this.$refs.svg1)
                .html('') // 清除之前的图表
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", `translate(${width / 2}, ${height / 2})`);

            svg1.selectAll('.arc').remove(); // 清除
            // 创建弧生成器
            const arc = d3.arc()
                .innerRadius(radius * 0.3) // 内半径
                .outerRadius(radius); // 外半径

            // 创建饼图布局
            const pie = d3.pie()
                .value(d => d.value)
                .sort(null); // 不排序
            console.log(pie(dataForChart));
            // 绘制弧
            svg1.selectAll(".arc")
                .data(pie(dataForChart))
                .enter()
                .append("path")
                .attr("d", arc)
                .attr("fill", d => color(d.data.label))
                .attr("stroke", "black")
                .attr("stroke-width", 1)
                .on("mouseover", function (event, d) {
                    // 鼠标悬停时，高亮显示当前区域
                    d3.select(this)
                        .attr('fill', 'orange') // 改变填充颜色为高亮色，比如橙色
                        .attr('stroke-width', 2) // 增加边框宽度
                        .attr('stroke', 'red'); // 改变边框颜色

                    // 当鼠标悬停时，计算并显示百分比
                    const total = dataForChart.reduce((sum, item) => sum + item.value, 0);
                    const percentage = ((d.value / total) * 100).toFixed(2);

                    // 在此处添加显示百分比的逻辑，例如通过tooltip或修改现有元素的内容
                    // 以下是一个简单的示例，它在控制台打印百分比（实际应用中可能需要更复杂的UI展示）
                    console.log(`${d.data.label}: ${percentage}%`);

                    // 假设我们有一个用于显示tooltip的div
                    const tooltip = d3.select("#tooltip1");
                    tooltip.style("opacity", 1) // 设置透明度使其可见
                        .style("left", `${event.pageX + 10}px`) // 定位tooltip
                        .style("top", `${event.pageY - 10}px`)
                        .text(`${d.data.label}: ${percentage}%`); // 设置tooltip的文本内容
                })
                .on("mouseout", function () {
                    d3.select(this)
                        .attr('fill', d => color(d.data.label)) // 恢复原始填充颜色
                        .attr('stroke-width', 1) // 恢复原始边框宽度
                        .attr('stroke', 'black'); // 恢复原始边框颜色
                    
                    // 当鼠标移开时，隐藏百分比显示
                    // 假设我们有一个用于显示tooltip的div
                    const tooltip = d3.select("#tooltip1");
                    tooltip.style("opacity", 0); // 设置透明度隐藏tooltip
                });

            // 添加图例
            const legend = svg1.selectAll(".legend")
                .data(dataForChart)
                .enter()
                .append("g")
                .attr("class", "legend")
                .attr("transform", (d, i) => `translate(${-width / 2 + 20}, ${height / 2 - (i + 1) * 20})`);

            legend.append("rect")
                .attr("width", 18)
                .attr("height", 18)
                .attr("fill", d => color(d.label));

            legend.append("text")
                .attr("x", 24)
                .attr("y", 9)
                .attr("dy", ".35em")
                .text(d => d.label);
        },

        // 过滤数据
        filterRatioData() {
            const { rawRatioData, selectedCompany, selectedTimeRange } = this;
            const startDate = selectedTimeRange.start;
            const endDate = selectedTimeRange.end;

            // 过滤出符合公司和时间段条件的数据
            this.filteredRatioData = rawRatioData.filter(d => {
                const filingDate = d.filing_date;
                return d.original_organization === selectedCompany &&
                    filingDate >= startDate &&
                    filingDate <= endDate;
            });
        },
        // 渲染图表
        renderRatioChart() {
            const { filteredRatioData, chartConfig2 } = this;
            if (filteredRatioData.length === 0) {
                return; // 没有数据则不渲染图表
            }

            const { width, height, radius, colors } = chartConfig2;
            const svg2 = d3.select(this.$refs.svg2)
                .html('') // 清除之前的图表
                .append('svg')
                .attr('width', width)
                .attr('height', height)
                .append('g')
                .attr('transform', `translate(${width / 2}, ${height / 2})`);

            // 计算男女发明人的数量
            const maleCount = filteredRatioData.filter(d => d.male_flag === '1.0').length;
            const femaleCount = filteredRatioData.filter(d => d.male_flag === '0.0').length;

            // 创建饼图数据
            const pieRatioData = [
                { label: 'Male', value: maleCount },
                { label: 'Female', value: femaleCount }
            ];

            // 创建饼图生成器
            const pie = d3.pie()
                .value(d => d.value)
                .sort(null);

            // 创建弧生成器
            const arc = d3.arc()
                .innerRadius(radius * 0.3)
                .outerRadius(radius);

            // 绘制饼图
            svg2.selectAll('path')
                .data(pie(pieRatioData))
                .enter()
                .append('path')
                .attr('d', arc)
                .attr('fill', (d, i) => colors[i])
                .attr("stroke", "black")
                .attr("stroke-width", 1)
                .on("mouseover", function (event, d) {
                    // 鼠标悬停时，计算百分比并展示
                    const total = pieRatioData.reduce((sum, item) => sum + item.value, 0);
                    const percentage = ((d.value / total) * 100).toFixed(2);

                    // 展示百分比的逻辑，例如通过tooltip
                    // 假设我们有一个ID为'tooltip'的元素用于显示tooltip
                    const tooltip = d3.select("#tooltip2");
                    tooltip.style("opacity", 1) // 设置为可见
                        .style("left", `${event.pageX + 10}px`) // 定位tooltip
                        .style("top", `${event.pageY - 10}px`)
                        .text(`${d.data.label}: ${percentage}%`); // 设置tooltip内容
                })
                .on("mouseout", function () {
                    // 鼠标移开时，隐藏百分比显示
                    const tooltip = d3.select("#tooltip2");
                    tooltip.style("opacity", 0); // 隐藏tooltip
                });

            // 添加图例
            const legend = svg2.selectAll('.legend')
                .data(pieRatioData)
                .enter()
                .append('g')
                .attr('class', 'legend')
                .attr('transform', (d, i) => `translate(${radius + 20}, ${i * 25 + 10})`);

            legend.append('rect')
                .attr('width', 18)
                .attr('height', 18)
                .attr('fill', (d, i) => colors[i]);

            legend.append('text')
                .attr('x', 24)
                .attr('y', 14)
                .text(d => d.label);
        },
        // 过滤数据并渲染图表
        filterDataAndRenderChart() {
            this.filterRatioData();
            this.renderRatioChart();
        },

        updateClassTableData() {
            const { rawClassData, selectedCompany, selectedTimeRange } = this;
            const startDate = selectedTimeRange.start;
            const endDate = selectedTimeRange.end;

            const filteredClassData = rawClassData.filter(
                d => d.original_organization === selectedCompany &&
                    d.filing_date >= startDate &&
                    d.filing_date <= endDate
            );

            const cpcClassCounts = filteredClassData.reduce((acc, row) => {
                acc[row.cpc_class] = (acc[row.cpc_class] || 0) + 1;
                return acc;
            }, {});

            const tableDataArray = Object.entries(cpcClassCounts).map(([cpc_class, count]) => ({
                cpc_class,
                count_of_cpc_class: count
            }));

            tableDataArray.sort((a, b) => b.count_of_cpc_class - a.count_of_cpc_class);

            this.tableData = tableDataArray.slice(0, 10);
        },
    },
};