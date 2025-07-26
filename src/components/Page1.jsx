import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { ChevronLeft, ChevronRight, Calendar } from 'lucide-react';
import Table from './Table';
import './page.css';

const Page1 = () => {
  const chartRef = useRef();
  const [currentChart, setCurrentChart] = useState(0);
  const [selectedYear, setSelectedYear] = useState('2024');
  const [tableData, setTableData] = useState(null);
  const [tableYear, setTableYear] = useState('2023-24');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chartData, setChartData] = useState({});
  const [chartLoading, setChartLoading] = useState(false);
  const [chartError, setChartError] = useState(null);

  const chartYears = [
    '2025-26', '2024-25', '2023-24', '2022-23', '2021-22', 
    '2020-21', '2019-20', '2018-19', '2017-18'
  ];
  const tableYears = [
    '2025-26', '2024-25', '2023-24', '2022-23', '2021-22', 
    '2020-21', '2019-20', '2018-19', '2017-18'
  ];
  const chartTitles = ['Monthly Performance Trend', 'Product Performance Analysis'];

  const fetchChartData = async (year) => {
    setChartLoading(true);
    setChartError(null);
    try {
      const [lineRes, barRes] = await Promise.all([
        fetch(`http://localhost:5000/api/chart-data?year=${year}&chartType=line`),
        fetch(`http://localhost:5000/api/chart-data?year=${year}&chartType=bar`)
      ]);

      if (!lineRes.ok || !barRes.ok) {
        throw new Error('Failed to fetch chart data');
      }

      const lineData = await lineRes.json();
      const barData = await barRes.json();

      setChartData(prev => ({
        ...prev,
        [year]: {
          line: lineData.line || [],
          bar: barData.bar || []
        }
      }));
    } catch (err) {
      setChartError(err.message);
      console.error('Error fetching chart data:', err);
    } finally {
      setChartLoading(false);
    }
  };

  const fetchTableData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/api/traffic-data?selectedYear=${tableYear}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setTableData(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching table data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!chartData[selectedYear]) {
      fetchChartData(selectedYear);
    }
    drawChart();
  }, [currentChart, selectedYear, chartData]);

  useEffect(() => {
    fetchTableData();
  }, [tableYear]);

  const drawChart = () => {
    if (currentChart === 0) {
      drawLineChart();
    } else {
      drawBarChart();
    }
  };

  const drawLineChart = () => {
    const svg = d3.select(chartRef.current);
    svg.selectAll("*").remove();

    if (chartLoading || !chartData[selectedYear]?.line) {
      svg.append('text')
        .attr('x', 360)
        .attr('y', 200)
        .attr('text-anchor', 'middle')
        .text(chartLoading ? 'Loading chart data...' : 'No data available');
      return;
    }

    const margin = { top: 40, right: 40, bottom: 60, left: 70 };
    const width = 680 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const chart = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const lineData = chartData[selectedYear].line;

    const x = d3.scaleBand()
      .domain(lineData.map(d => d.month))
      .range([0, width])
      .padding(0.2);

    const y = d3.scaleLinear()
      .domain([0, d3.max(lineData, d => d.value) + 10])
      .range([height, 0]);

    chart.selectAll('.grid-line-y')
      .data(y.ticks(5))
      .enter().append('line')
      .attr('class', 'grid-line-y')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', d => y(d))
      .attr('y2', d => y(d))
      .attr('stroke', '#f8fafc')
      .attr('stroke-width', 1);

    const area = d3.area()
      .x(d => x(d.month) + x.bandwidth() / 2)
      .y0(height)
      .y1(d => y(d.value))
      .curve(d3.curveCatmullRom.alpha(0.5));

    chart.append('path')
      .datum(lineData)
      .attr('fill', '#6366f1')
      .attr('fill-opacity', 0.03)
      .attr('d', area);

    const line = d3.line()
      .x(d => x(d.month) + x.bandwidth() / 2)
      .y(d => y(d.value))
      .curve(d3.curveCatmullRom.alpha(0.5));

    const path = chart.append('path')
      .datum(lineData)
      .attr('fill', 'none')
      .attr('stroke', '#6366f1')
      .attr('stroke-width', 2)
      .attr('d', line)
      .attr('stroke-dasharray', function() {
        return this.getTotalLength();
      })
      .attr('stroke-dashoffset', function() {
        return this.getTotalLength();
      })
      .transition()
      .duration(1200)
      .ease(d3.easeQuadOut)
      .attr('stroke-dashoffset', 0);

    chart.selectAll('.dot')
      .data(lineData)
      .enter().append('circle')
      .attr('class', 'dot')
      .attr('cx', d => x(d.month) + x.bandwidth() / 2)
      .attr('cy', d => y(d.value))
      .attr('r', 0)
      .attr('fill', '#6366f1')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .transition()
      .delay((d, i) => i * 60)
      .duration(300)
      .attr('r', 3);

    chart.selectAll('.dot')
      .on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(150)
          .attr('r', 5)
          .attr('fill', '#4f46e5');

        chart.append('g')
          .attr('class', 'tooltip')
          .append('rect')
          .attr('x', x(d.month) + x.bandwidth() / 2 - 20)
          .attr('y', y(d.value) - 30)
          .attr('width', 40)
          .attr('height', 20)
          .attr('fill', '#1f2937')
          .attr('rx', 3)
          .attr('opacity', 0)
          .transition()
          .duration(150)
          .attr('opacity', 0.9);

        chart.select('.tooltip')
          .append('text')
          .attr('x', x(d.month) + x.bandwidth() / 2)
          .attr('y', y(d.value) - 16)
          .attr('text-anchor', 'middle')
          .style('font-size', '11px')
          .style('font-weight', '500')
          .style('fill', '#ffffff')
          .style('opacity', 0)
          .text(d.value)
          .transition()
          .duration(150)
          .style('opacity', 1);
      })
      .on('mouseout', function(event, d) {
        d3.select(this)
          .transition()
          .duration(150)
          .attr('r', 3)
          .attr('fill', '#6366f1');

        chart.selectAll('.tooltip')
          .transition()
          .duration(150)
          .style('opacity', 0)
          .remove();
      });

    chart.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('font-size', '11px')
      .style('font-weight', '400')
      .style('fill', '#6b7280');

    chart.append('g')
      .attr('class', 'y-axis')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d))
      .selectAll('text')
      .style('font-size', '11px')
      .style('font-weight', '400')
      .style('fill', '#6b7280');

    chart.selectAll('.domain').attr('stroke', '#e5e7eb').attr('stroke-width', 1);
    chart.selectAll('.tick line').attr('stroke', '#e5e7eb').attr('stroke-width', 1);

    chart.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -45)
      .attr('x', -height / 2)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('fill', '#9ca3af')
      .style('font-weight', '400')
      .text('Performance Score');
  };

  const drawBarChart = () => {
    const svg = d3.select(chartRef.current);
    svg.selectAll("*").remove();

    if (chartLoading || !chartData[selectedYear]?.bar) {
      svg.append('text')
        .attr('x', 360)
        .attr('y', 200)
        .attr('text-anchor', 'middle')
        .text(chartLoading ? 'Loading chart data...' : 'No data available');
      return;
    }

    const margin = { top: 40, right: 40, bottom: 60, left: 70 };
    const width = 680 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const chart = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const barData = chartData[selectedYear].bar;

    const x = d3.scaleBand()
      .domain(barData.map(d => d.category))
      .range([0, width])
      .padding(0.4);

    const y = d3.scaleLinear()
      .domain([0, d3.max(barData, d => d.value) + 10])
      .range([height, 0]);

    chart.selectAll('.grid-line-y')
      .data(y.ticks(5))
      .enter().append('line')
      .attr('class', 'grid-line-y')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', d => y(d))
      .attr('y2', d => y(d))
      .attr('stroke', '#f8fafc')
      .attr('stroke-width', 1);

    chart.selectAll('.bar')
      .data(barData)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.category))
      .attr('y', height)
      .attr('width', x.bandwidth())
      .attr('height', 0)
      .attr('fill', '#6366f1')
      .attr('rx', 2)
      .style('cursor', 'pointer')
      .transition()
      .delay((d, i) => i * 100)
      .duration(600)
      .ease(d3.easeQuadOut)
      .attr('y', d => y(d.value))
      .attr('height', d => height - y(d.value));

    chart.selectAll('.label')
      .data(barData)
      .enter().append('text')
      .attr('class', 'label')
      .attr('x', d => x(d.category) + x.bandwidth() / 2)
      .attr('y', height)
      .attr('text-anchor', 'middle')
      .style('font-size', '11px')
      .style('font-weight', '500')
      .style('fill', '#6b7280')
      .style('opacity', 0)
      .text(d => d.value)
      .transition()
      .delay((d, i) => i * 100 + 300)
      .duration(300)
      .attr('y', d => y(d.value) - 8)
      .style('opacity', 1);

    chart.selectAll('.bar')
      .on('mouseover', function(event, d) {
        d3.select(this)
          .transition()
          .duration(150)
          .attr('fill', '#4f46e5')
          .style('opacity', 0.8);
      })
      .on('mouseout', function(event, d) {
        d3.select(this)
          .transition()
          .duration(150)
          .attr('fill', '#6366f1')
          .style('opacity', 1);
      });

    chart.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .style('font-size', '11px')
      .style('font-weight', '400')
      .style('fill', '#6b7280');

    chart.append('g')
      .attr('class', 'y-axis')
      .call(d3.axisLeft(y).ticks(5).tickFormat(d => d))
      .selectAll('text')
      .style('font-size', '11px')
      .style('font-weight', '400')
      .style('fill', '#6b7280');

    chart.selectAll('.domain').attr('stroke', '#e5e7eb').attr('stroke-width', 1);
    chart.selectAll('.tick line').attr('stroke', '#e5e7eb').attr('stroke-width', 1);

    chart.append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -45)
      .attr('x', -height / 2)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('fill', '#9ca3af')
      .style('font-weight', '400')
      .text('Performance Score');
  };

  const nextChart = () => {
    setCurrentChart((prev) => (prev + 1) % chartTitles.length);
  };

  const prevChart = () => {
    setCurrentChart((prev) => (prev - 1 + chartTitles.length) % chartTitles.length);
  };

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <h1 className="dashboard-title">Performance Analytics</h1>
        <div className="year-selector">
          <Calendar size={16} color="#6b7280" />
          <select 
            value={selectedYear} 
            onChange={(e) => setSelectedYear(e.target.value)}
            className="year-dropdown"
          >
            {chartYears.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="chart-container">
        <div className="chart-header">
          <button 
            onClick={prevChart} 
            className="nav-button"
            disabled={currentChart === 0}
          >
            <ChevronLeft size={18} />
          </button>
          
          <h2 className="chart-title">
            {chartTitles[currentChart]} • {selectedYear}
          </h2>
          
          <button 
            onClick={nextChart} 
            className="nav-button"
            disabled={currentChart === chartTitles.length - 1}
          >
            <ChevronRight size={18} />
          </button>
        </div>

        <div className="chart-wrapper">
          {chartError && (
            <div className="error-message">Chart Error: {chartError}</div>
          )}
          <svg ref={chartRef} width={720} height={440} />
        </div>

        <div className="chart-indicators">
          {chartTitles.map((_, index) => (
            <button
              key={index}
              className={`indicator ${currentChart === index ? 'active' : ''}`}
              onClick={() => setCurrentChart(index)}
            />
          ))}
        </div>

        <div className="table-section">
          <div className="table-header">
            <h3 className="table-title">Goods Traffic Pattern</h3>
            <select
              value={tableYear}
              onChange={(e) => setTableYear(e.target.value)}
              className="year-dropdown"
            >
              {tableYears.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          {loading && <div className="loading-message">Loading data...</div>}
          {error && <div className="error-message">Error: {error}</div>}
          {tableData && <Table data={tableData} />}
        </div>
      </div>
    </div>
  );
};

export default Page1;