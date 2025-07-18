import * as d3 from "d3";
import { EventBus } from '../eventbus'; // 引入 EventBus

export default {
    name: "ChordDiagram",
    data() {
        return {
            rawData: [],
            filteredData: [],
            selectedCompanies: [],
            uniqueCompanies: [],
            filteredOptions: [],
            filterActive: [],
            width: 700,
            height: 700,
            colorScale: d3.scaleOrdinal(d3.schemeCategory10), // 颜色映射
            inventorTableData: [], // 用来存储人员信息的表格数据
            firstColumn: [],         // 第一列 inventorIds
            secondColumn: [],        // 第二列 inventorIds
            thirdColumn: [],         // 第三列 inventorIds
            inventorTableDataAll: [], // 存储发明人信息
            inventorTableDataAllByYear: [], //按年份存贮发明人信息
            colorScaleHeatMap: d3.scaleLinear().domain([0, 100]).range(["#ffffff", "#ff0000"]), // 用于生成热力图的颜色范围
            hoveredInventor: null, // 当前悬停的发明人数据
            yearRange: null,     // 存储年份范围
        };
    },
    mounted() {
        this.loadData();
        this.loadInventorData();
        this.loadInventorDataByYear();
        console.log('数据加载完成，开始监听事件');
        // 监听 time-range-selected 事件
        EventBus.on('time-range-selected', this.handleTimeRangeSelection);
        
    },
    beforeDestroy() {
        // 组件销毁时移除事件监听器
        EventBus.off('time-range-selected', this.handleTimeRangeSelection);
    },
    methods: {
        async loadData() {
            const csvData = await d3.csv("static/yearly_aggregated_mobility_data_with_inventors.csv");

            if (this.yearRange) {
                const { start, end } = this.yearRange;

                this.rawData = csvData.map((row) => ({
                    previous_organization: row.previous_organization,
                    original_organization: row.original_organization,
                    inventor_count: +row.inventor_count,
                    inventor_ids: row.inventor_ids.replace(/\[/g,'').replace(/\]/g,'').replace(/'/g,'').split(','),
                    year: +row.year, // 假设数据中有 `year` 字段
                })).filter((d) => d.year >= start && d.year <= end); // 根据年份范围过滤数据
            } else {
                this.rawData = csvData.map((row) => ({
                    previous_organization: row.previous_organization,
                    original_organization: row.original_organization,
                    inventor_count: +row.inventor_count,
                    inventor_ids: row.inventor_ids
                        .replace(/\[/g, "")
                        .replace(/\]/g, "")
                        .replace(/'/g, "")
                        .split(","),
                    year: +row.year,
                }));
            }

            this.uniqueCompanies = Array.from(
                new Set([
                    ...this.rawData.map((d) => d.previous_organization),
                    ...this.rawData.map((d) => d.original_organization),
                ])
            );

            // 默认选择前三家公司
            this.selectedCompanies = ["Apple Inc.","Google Inc."];
            //this.selectedCompanies = this.uniqueCompanies.slice(0, 3);
            this.filteredOptions = this.selectedCompanies.map(() => [...this.uniqueCompanies]);
            this.filterActive = Array(this.selectedCompanies.length).fill(false);
            this.addDotPattern(); // 添加点状填充模式
            this.updateChart();
            
        },

        async loadInventorData() {
            const data = await d3.csv("static/processed_data_inventor.csv");
            console.log(data[1]);
            this.inventorTableDataAll = data;
        },
        async loadInventorDataByYear() {
            const data = await d3.json("static/prepared_data.json");
            
            this.inventorTableDataAllByYear = data;
            console.log(this.inventorTableDataAllByYear);
        },
        // 计算颜色背景
        getColorForInventor(patentCount, citedCount) {
            // 合成一个值来确定颜色
            const score = patentCount + citedCount; // 或者按其他方式计算
            return this.colorScale(score);
        },

        addDotPattern() {
            const svg = d3.select(this.$refs.svg);

            // 添加一个小点到圆形的中心
            svg.append("circle")
                .attr("cx", 20)  // 点的水平位置
                .attr("cy", 20)  // 点的垂直位置
                .attr("r", 2)   // 点的半径
                .style("fill", "#000000") // 点的颜色
                .attr("class", "center-dot"); // 添加类名以便管理
            //console.log('数据加载完成，开始监听事件',);
        },

        onCompanyChange(index) {
            index;
            this.updateChart();
        },
        addCompany() {
            if (this.selectedCompanies.length < this.uniqueCompanies.length) {
                this.selectedCompanies.push("");
                this.filteredOptions.push([...this.uniqueCompanies]);
                this.filterActive.push(false);
            }
        },
        removeSelector(index) {
            // 删除当前选择框
            this.selectedCompanies.splice(index, 1);
            this.filteredOptions.splice(index, 1);
            this.filterActive.splice(index, 1);
            this.updateChart();
        },
        toggleFilter(index) {
            // 切换筛选状态
            this.filterActive[index] = !this.filterActive[index];

            if (this.filterActive[index]) {
                // 筛选公司
                const relatedCompanies = new Set();

                for (let i = 0; i < index; i++) {
                    const currentCompany = this.selectedCompanies[i];
                    this.rawData.forEach((row) => {
                        if (row.previous_organization === currentCompany) {
                            relatedCompanies.add(row.original_organization);
                        }
                        if (row.original_organization === currentCompany) {
                            relatedCompanies.add(row.previous_organization);
                        }
                    });
                }

                this.filteredOptions[index] = Array.from(relatedCompanies);
                this.$nextTick(() => {
                    const button = this.$el.querySelectorAll('.filter-button')[index];
                    button.classList.add('active');  // 激活小点
                });
            } else {
                // 取消筛选
                this.filteredOptions[index] = [...this.uniqueCompanies];
                this.$nextTick(() => {
                    const button = this.$el.querySelectorAll('.filter-button')[index];
                    button.classList.remove('active');  // 取消小点
                });
            }
            this.updateChart();
        },

        // 处理接收到的时间范围选择事件
        handleTimeRangeSelection(timeRange) {
            this.yearRange = timeRange; // 更新年份范围
            console.log('E 接收到时间范围:', timeRange);
            this.loadData(); // 重新加载数据并过滤
        },
        updateChart() {
            this.filteredData = this.rawData.filter(
                (d) =>
                    this.selectedCompanies.includes(d.previous_organization) &&
                    this.selectedCompanies.includes(d.original_organization)
            );

            this.renderChart();
            
        },
        renderChart() {
            const data = this.filteredData;
            console.log(data);
            const { width, height } = this;

            d3.select(this.$refs.svg).selectAll("*").remove();

            if (!Array.isArray(data) || data.length === 0) {
                console.error("No data to display. Please select valid companies.");
                return;
            }

            const innerRadius = Math.min(width, height) * 0.4;
            const outerRadius = innerRadius + 10;

            const svg = d3
                .select(this.$refs.svg)
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", `translate(${width / 2}, ${height / 2})`);

            const organizations = Array.from(
                new Set(
                    data.reduce((acc, d) => {
                        acc.push(d.previous_organization, d.original_organization);
                        return acc;
                    }, [])
                )
            );

            const organizationIndex = new Map(
                organizations.map((org, i) => [org, i])
            );

            const matrix = Array.from({ length: organizations.length }, () =>
                Array(organizations.length).fill(0)
            );

            data.forEach(({ previous_organization, original_organization, inventor_count }) => {
                const source = organizationIndex.get(previous_organization);
                const target = organizationIndex.get(original_organization);
                matrix[source][target] += inventor_count;
            });

            const chord = d3
                .chord()
                .padAngle(0.05)
                .sortSubgroups(d3.descending)(matrix);
            //弧形路径生成器
            const arc = d3.arc().innerRadius(innerRadius).outerRadius(outerRadius);
            //连线路径生成器
            const ribbon = d3.ribbon().radius(innerRadius);
            //颜色映射
            const color = this.colorScale;
            //弧形
            svg
                .append("g")
                .selectAll("path")
                .data(chord.groups)
                .join("path")
                .style("fill", (d) => color(organizations[d.index]))
                .style("stroke", (d) => d3.rgb(color(organizations[d.index])).darker())
                .attr("d", arc)
                .on("mouseover", (event, d) => {
                    // 高亮当前弦
                    d3.select(event.target)
                        .style("fill", d3.rgb(color(organizations[d.index])).darker())
                        .style("stroke", "black")
                        .style("opacity", 1);
                })
                .on("mouseout", (event, d) => {
                    // 恢复弦颜色
                    d3.select(event.target)
                        .style("fill", color(organizations[d.index]))
                        .style("stroke", d3.rgb(color(organizations[d.index])).darker())
                        .style("opacity", 0.7);
                });
            //公司名称标签
            svg
                .append("g")
                .selectAll("text")
                .data(chord.groups)
                .join("text")
                .attr("transform", (d) => {
                    const angle = (d.startAngle + d.endAngle) / 2;
                    const x = Math.sin(angle) * (outerRadius + 20);
                    const y = -Math.cos(angle) * (outerRadius + 20);
                    return `translate(${x}, ${y})`;
                })
                .attr("text-anchor", (d) =>
                    (d.startAngle + d.endAngle) / 2 > Math.PI ? "end" : "start"
                )
                .attr("alignment-baseline", "middle")
                .text((d) => organizations[d.index])
                .style("font-size", "12px")
                .style("fill", "#000");
            //绘制弧形路径
            svg
                .append("g")
                .selectAll("path")
                .data(chord)
                .join("path")
                .attr("d", ribbon)
                .style("fill", (d) => color(organizations[d.target.index]))
                .style("stroke", (d) => d3.rgb(color(organizations[d.target.index])).darker())
                .style("opacity", 0.7)
                .attr("class", "ribbon")
                .on("click", (event, d) => {
                    // 获取被点击的弦的相关人员信息
                    const inventorIds = data.filter(
                        (row) =>
                            row.previous_organization === organizations[d.source.index] &&
                            row.original_organization === organizations[d.target.index]
                    ).map((row) => row.inventor_ids).flat();
                    // 更新人员信息表
                    this.updateInventorTable(inventorIds);
                    this.drawLineChart();
                })
                .on("mouseover", event => {
                    // 高亮当前弦
                    d3.select(event.target)
                        .style("opacity", 1);
                })
                .on("mouseout", event => {
                    // 恢复弦颜色
                    d3.select(event.target)
                        .style("opacity", 0.7);
                });

        },
        // 更新人员信息表格
        updateInventorTable(inventorIds) {
            // 将 inventorIds 数据更新到 Vue 的 data 中
            this.splitInventorIds(inventorIds);   // 分割数据到两列
            this.inventorTableData = inventorIds;
            console.log(inventorIds);
        },
        splitInventorIds(inventorIds) {
            const third = Math.floor(inventorIds.length / 3+1);
            const second = Math.floor(inventorIds.length * 2 / 3+1);

            this.firstColumn = inventorIds.slice(0, third);         // 第一列
            this.secondColumn = inventorIds.slice(third, second);    // 第二列
            this.thirdColumn = inventorIds.slice(second);            // 第三列
            console.log(this.firstColumn);
            console.log(this.secondColumn);
            console.log(this.thirdColumn);
        },
        getInventorInfo(id) {
            // 查找 inventorTableDataAll 中与 id 匹配的发明人信息
            const inventor = this.inventorTableDataAll.find(item => item.inventor_id === id);
            // 返回要显示的信息（可以根据需要调整显示内容）
            return inventor ? `Name: ${inventor.inventor_id}, Patents: ${inventor.patent_ids}, beCited: ${inventor.beCited}` : 'No data available';
        },
        drawLineChart() {
            const margin = { top: 20, right: 30, bottom: 50, left: 50 };
            const width = 700 - margin.left - margin.right;
            const height = 400 - margin.top - margin.bottom;

            // 清除现有图表（防止重叠）
            d3.select("#line-chart").selectAll("*").remove();

            // 创建SVG容器
            const svg = d3
                .select("#line-chart")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", `translate(${margin.left},${margin.top})`);

            // 筛选出只包含在 inventorTableData 中的发明人数据
            const inventorSet = new Set(this.inventorTableData); // 创建一个包含表格数据的集合
            const filteredData = this.inventorTableDataAllByYear.filter((employee) =>
                inventorSet.has(employee.id)
            );

            // 提取所有年份并排序
            const years = Array.from(
                new Set(
                    filteredData.flatMap((d) => d.publications.map((p) => p.year))
                )
            ).sort((a, b) => a - b);

            // 准备数据：将每个发明人的数据填充为每年都包含（不存在的数据置为0）
            const data = filteredData.map((employee) => {
                const yearData = Object.fromEntries(
                    employee.publications.map((p) => [p.year, p.count])
                );
                return {
                    id: employee.id,
                    values: years.map((year) => ({ year, count: yearData[year] || 0 })),
                };
            });

            if (data.length === 0) {
                console.warn("No data available for the selected inventors.");
                return;
            }

            // 为每个年份创建比例尺
            const xScale = d3
                .scalePoint()
                .domain(years)
                .range([0, width])
                .padding(1);

            const yScale = d3
                .scaleLinear()
                .domain([0, d3.max(data.flatMap((d) => d.values.map((v) => v.count)))]).nice()
                .range([height, 0]);

            // 绘制每个年份的轴
            svg.selectAll(".dimension")
                .data(years)
                .enter()
                .append("g")
                .attr("class", "dimension")
                .attr("transform", (d) => `translate(${xScale(d)},0)`)
                .each(function (year, i) {
                    const axis = d3.axisLeft(yScale);
                    if (i !== 0) {
                        axis.tickFormat(() => ""); // 隐藏非第一个Y轴的刻度
                    }
                    d3.select(this).call(axis);
                })
                .append("text")
                .attr("class", "axis-label")
                .attr("y", -10)
                .attr("x", -5)
                .style("text-anchor", "middle")
                .text((d) => d);

            // 绘制数据的线条
            const line = d3
                .line()
                .x((d) => xScale(d.year))
                .y((d) => yScale(d.count));

            svg.selectAll(".line")
                .data(data)
                .enter()
                .append("path")
                .attr("class", "line")
                .attr("d", (d) => line(d.values))
                .attr("fill", "none")
                .attr("stroke", d3.schemeCategory10[Math.floor(Math.random() * 10)])
                .attr("stroke-width", 1.5)
                .append("title") // Tooltip显示ID
                .text((d) => d.id);
        }
    },
};