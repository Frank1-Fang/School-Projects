Code used to implement our interactive web-based dashboard.

# Code Overview: Data Visualization Final Project

This directory contains the Vue + D3.js source code for our **final project in the Data Visualization course (ARTS1422)** at ShanghaiTech University.  
Our project explores career development trends and research behavior through US patent data from 1989 to 2020.

I (Youzheng Fang) was responsible for implementing the **ABC three-part interactive visualization system**, described below.

## Section A – Yearly Patent Trend Line Chart

**File**: `sectionA/script.js`  
**Function**: Draws an interactive **line chart** that shows the yearly count of patents across all organizations.

### Features:
- Uses `d3.line()` to render patent trend over time
- Highlights selected time range via **brush** interaction
- Emits a time range event via `EventBus` for downstream filtering
- Tooltip on hover shows:
  - Year
  - Number of patents
- Debounced event broadcasting to avoid excessive triggers

### Data:
- `patent_yearly_counts.csv`

## Section B – PCA Clustered Organization Scatterplot

**File**: `sectionB/script.js`  
**Function**: Renders a **scatterplot of organizations clustered by research behavior**, using PCA-reduced features.

### Features:
- Each dot represents an organization, color-coded by cluster
- Tooltip on hover shows:
  - Institution name
  - Cluster label
- Clicking a bar in Section C will **highlight the corresponding cluster** and selected organization in red
- Scales and axes are manually adjusted for better readability

### Data:
- `pca_clustered_data.csv`

## Section C – Institution Bar Chart by Field & Metric

**File**: `sectionC/script.js`  
**Function**: Displays a vertical scrollable **bar chart comparing institutions** by patent count or citation count.

### Features:
- Each row = one organization
- Two bars per row:
  - 🟣 Citation count (top)
  - 🟡 Patent count (bottom)
- Color-coded by metric, with hoverable tooltips
- Custom dropdown for:
  - Field-based filtering (e.g., specific CPC sub-classes)
  - Metric switching (`patent` / `citation`)
- Search box with intelligent auto-complete and scrolling
- Responds to **time range selection** from Section A and **sends institution events** to Section B via `EventBus`

### Data:
- `institution_patent_counts.csv`
- `institution_citation_counts.csv`
- `institution_analysis_unique.csv`
- `year_org_class_cite.csv`

## Tech Stack

| Layer       | Tools                |
|-------------|----------------------|
| Frontend    | `Vue.js`, `D3.js v7` |
| Data Format | `CSV`, `JavaScript Object` |
| Communication | Custom `EventBus` for decoupled messaging between sections |
| Tooling     | Manual scales, tooltips, SVG manipulation, scrollable containers |
