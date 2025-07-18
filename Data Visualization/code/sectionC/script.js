import * as d3 from 'd3';
import { EventBus } from '../eventbus';

export default {
    data() {
        return {
            // 图表参数
            width: 800,
            height: 950,
            margin: { top: 20, right: 30, bottom: 70, left: 50 },

            // 数据相关变量
            allData: [], // 存储所有处理过的数据
            filteredData: [], // 筛选后的数据
            searchQuery: "", // 用户输入的搜索内容
            suggestions: [], // 存储智能提示列表
            hoveredSuggestion: null, // 用于高亮当前悬浮的建议项

            selectedField: "", // 当前选择的细分领域
            selectedMetric: "patent", // 当前选择的数据类型（专利数/引用数）
            availableFields: [], // 可用的细分领域
        };
    },
    async mounted() {
        try {
            // 异步加载 CSV 文件
            const patentData = await d3.csv('../../../static/institution_patent_counts.csv');
            const citationData = await d3.csv('../../../static/institution_citation_counts.csv');
            const institutionTags = await d3.csv('../../../static/institution_analysis_unique.csv');

            // 处理原始数据
            const processedData = this.processData(patentData, citationData, institutionTags);

            // 初始化可选的细分领域
            this.availableFields = Array.from(new Set(institutionTags.map((tag) => tag.max_patent_cpc_sub_class)));

            // 初始化
            this.allData = processedData;
            this.filteredData = processedData;

            // 绘制初始图表
            this.drawBarChart(this.filteredData);

            //await this.loadData();
            console.log('数据加载完成，开始监听事件');
            EventBus.on('time-range-selected', this.handleTimeRangeUpdate);


        } catch (error) {
            console.error('Error loading CSV data:', error);
        }

    },

    unmounted() {
        // 移除事件监听器
        EventBus.off('time-range-selected', this.handleTimeRangeUpdate);
    },

    methods: {
        processData(patentData, citationData, institutionTags) {
            const processedData = patentData.map((patentRow) => {
                const institution = patentRow['original_organization'];
                const patentCounts = Object.keys(patentRow)
                    .slice(1)
                    .map((key) => +patentRow[key]);

                const citationRow = citationData.find(
                    (row) => row['original_organization'] === institution
                );

                const citationCounts = citationRow
                    ? Object.keys(citationRow)
                        .slice(1)
                        .map((key) => +citationRow[key])
                    : Array(patentCounts.length).fill(0);

                const tagRow = institutionTags.find(
                    (row) => row['original_organization'] === institution
                );

                return {
                    institution,
                    patentTotal: d3.sum(patentCounts),
                    citationTotal: d3.sum(citationCounts),
                    max_cited_cpc_sub_class: tagRow ? tagRow.max_cited_cpc_sub_class : 'N/A',
                    max_cited_count: tagRow ? +tagRow.max_cited_count : 0,
                    max_patent_cpc_sub_class: tagRow ? tagRow.max_patent_cpc_sub_class : 'N/A',
                    max_patent_count: tagRow ? +tagRow.max_patent_count : 0,
                };
            });

            processedData.sort((a, b) => b.citationTotal - a.citationTotal);

            return processedData;
        },

        handleSearch() {
            const query = this.searchQuery.trim();
            if (query) {
                // 找到匹配的机构索引
                const targetIndex = this.allData.findIndex((d) => d.institution === query);

                if (targetIndex !== -1) {
                    // 滚动到目标机构
                    const container = this.$refs.svgContainer;
                    const targetPosition = targetIndex * 100; // 假设每个条形图的高度是 100
                    container.scrollTo({ top: targetPosition, behavior: 'smooth' });
                }
            }
            this.suggestions = []; // 清空建议列表
            this.drawBarChart(this.filteredData);
        },


        updateSuggestions() {
            const query = this.searchQuery.trim().toLowerCase();
            if (query) {
                this.suggestions = this.allData
                    .map((d) => d.institution)
                    .filter((name) => name.toLowerCase().includes(query))
                    .slice(0, 10); // 限制最多显示10个建议
            } else {
                this.suggestions = [];
            }
        },

        selectSuggestion(suggestion) {
            this.searchQuery = suggestion; // 填充搜索框
            this.handleSearch(); // 执行搜索
        },

        async handleTimeRangeUpdate(range) {
            console.log('C 区域接收到的时间范围:', range);

            try {
                // 加载新数据
                const rawData = await d3.csv('../../../static/year_org_class_cite.csv');

                const { start, end } = range;

                // 筛选时间范围内的数据
                const filteredPatents = rawData.filter(
                    (d) => +d.filing_date >= start && +d.filing_date <= end
                );

                // 聚合数据：统计每个机构的领域专利数和引用数
                const aggregatedData = d3.group(filteredPatents, (d) => d.original_organization);

                const processedData = Array.from(aggregatedData, ([institution, records]) => {
                    // 按领域统计专利数
                    const patentCounts = d3.rollup(
                        records,
                        (v) => v.length,
                        (d) => d.cpc_sub_class
                    );

                    // 按领域统计引用数
                    const citationCounts = d3.rollup(
                        records,
                        (v) => d3.sum(v, (d) => +d.beCited),
                        (d) => d.cpc_sub_class
                    );

                    // 找到专利数最多的领域
                    const maxPatent = Array.from(patentCounts).reduce(
                        (acc, [key, value]) => (value > acc.count ? { field: key, count: value } : acc),
                        { field: 'N/A', count: 0 }
                    );

                    // 找到引用数最多的领域
                    const maxCitation = Array.from(citationCounts).reduce(
                        (acc, [key, value]) => (value > acc.count ? { field: key, count: value } : acc),
                        { field: 'N/A', count: 0 }
                    );

                    return {
                        institution,
                        patentTotal: d3.sum(records, () => 1), // 总专利数
                        citationTotal: d3.sum(records, (d) => +d.beCited), // 总引用数
                        max_patent_cpc_sub_class: maxPatent.field,
                        max_patent_count: maxPatent.count,
                        max_cited_cpc_sub_class: maxCitation.field,
                        max_cited_count: maxCitation.count,
                    };
                });

                // 对数据按引用总数降序排序
                this.filteredData = processedData.sort((a, b) => b.citationTotal - a.citationTotal);

                // 更新 `allData` 和 `suggestions` 以确保搜索功能正常
                this.allData = [...this.filteredData];
                this.updateSuggestions(); // 更新建议列表

                // 更新图表
                this.drawBarChart(this.filteredData);
            } catch (error) {
                console.error('重新加载数据失败:', error);
            }
        },

        updateBarChart() {
            console.log("当前选择的细分领域:", this.selectedField || "未选择任何领域");
            console.log("当前选择的指标:", this.selectedMetric);

            if (this.selectedField) {
                // 筛选在选定领域内的机构
                this.filteredData = this.allData.filter((d) =>
                    this.selectedMetric === "patent"
                        ? d.max_patent_cpc_sub_class === this.selectedField
                        : d.max_cited_cpc_sub_class === this.selectedField
                );

                // 根据选择的指标进行排序
                this.filteredData.sort((a, b) =>
                    this.selectedMetric === "patent"
                        ? b.max_patent_count - a.max_patent_count
                        : b.max_cited_count - a.max_cited_count
                );
            } else {
                // 如果未选择特定领域，恢复初始排序
                this.filteredData = [...this.allData].sort(
                    (a, b) =>
                        (this.selectedMetric === "patent"
                            ? b.patentTotal - a.patentTotal
                            : b.citationTotal - a.citationTotal)
                );
            }

            console.log("更新后的 filteredData:", this.filteredData);

            // 重新绘制图表
            this.drawBarChart(this.filteredData);
        },

        drawBarChart(data) {
            const { width, height, margin } = this;

            const barHeight = 100;
            const totalHeight = data.length * barHeight;

            const container = d3
                .select(this.$refs.svgContainer)
                .style('overflow-y', 'auto')
                .style('height', `${height}px`)
                .style('width', `${width}px`)
                .style('border', '1px solid #ccc');

            container.selectAll('*').remove(); // 清空之前的图表内容

            const svg = container
                .append('svg')
                .attr('width', width)
                .attr('height', totalHeight);

            const chartWidth = width - margin.left - margin.right;

            const xScale = d3
                .scaleLinear()
                .domain([0, d3.max(data, (d) => Math.max(d.patentTotal, d.citationTotal))])
                .range([0, chartWidth]);

            const yScale = d3
                .scaleBand()
                .domain(data.map((d) => d.institution))
                .range([0, totalHeight])
                .padding(0.2);

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

            const barGroups = svg
                .selectAll('.bar-group')
                .data(data)
                .join('g')
                .attr('class', 'bar-group')
                .attr('transform', (d) => `translate(${margin.left}, ${yScale(d.institution)})`);


            // 为每个单元添加边框
            barGroups
                .append('rect')
                .attr('class', 'unit-border')
                .attr('x', -margin.left + 50)
                .attr('y', -20)
                .attr('width', width - margin.right - 50)
                .attr('height', barHeight) // 单元高度，给文字留一点间距
                .attr('fill', 'none')
                .attr('stroke', '#ccc') // 边框颜色
                .attr('stroke-width', 1);

            barGroups.each(function (d) {
                const group = d3.select(this);

                group
                    .append('rect')
                    .attr('x', -margin.left) // 覆盖整个单元的宽度
                    .attr('y', 0)
                    .attr('width', width)
                    .attr('height', barHeight) // 覆盖整个单元的高度
                    .attr('fill', 'transparent') // 设置透明背景
                    .on('click', () => {
                        // 发送事件到 B 区域
                        EventBus.emit('institution-selected', d.institution);
                        console.log(`选中的机构: ${d.institution}`);
                    });

                group
                    .append('text')
                    .attr('x', 0)
                    .attr('y', -5)
                    .attr('text-anchor', 'start')
                    .attr('font-size', '12px')
                    .text(d.institution);

                group
                    .append('rect')
                    .attr('class', 'citation-bar')
                    .attr('x', 0)
                    .attr('y', 0)
                    .attr('width', xScale(d.citationTotal))
                    .attr('height', yScale.bandwidth() / 2)
                    .attr('fill', '#8B658B') // 引用数颜色
                    .on('mouseover', function (event) {
                        tooltip
                            .style('display', 'block')
                            .html(
                                `Institution: ${d.institution}<br>
                                # of citations: ${d.citationTotal}<br>
                                MAX citation: ${d.max_cited_cpc_sub_class} (${d.max_cited_count})`
                            )
                            .style('left', `${event.pageX + 10}px`)
                            .style('top', `${event.pageY + 10}px`);
                    })
                    .on('mouseout', function () {
                        tooltip.style('display', 'none');
                    });

                group
                    .append('rect')
                    .attr('class', 'patent-bar')
                    .attr('x', 0)
                    .attr('y', yScale.bandwidth() / 2)
                    .attr('width', xScale(d.patentTotal))
                    .attr('height', yScale.bandwidth() / 2)
                    .attr('fill', '#EEB422') // 专利数颜色
                    .on('mouseover', function (event) {
                        tooltip
                            .style('display', 'block')
                            .html(
                                `Institution: ${d.institution}<br>
                                # of patents: ${d.patentTotal}<br>
                                MAX patent: ${d.max_patent_cpc_sub_class} (${d.max_patent_count})`
                            )
                            .style('left', `${event.pageX + 10}px`)
                            .style('top', `${event.pageY + 10}px`);
                    })
                    .on('mouseout', function () {
                        tooltip.style('display', 'none');
                    });
            });

            svg.append('g')
                .attr('transform', `translate(${margin.left}, ${totalHeight})`)
                .call(d3.axisBottom(xScale).ticks(5).tickFormat(d3.format('.2s')));

        },

    },
};
