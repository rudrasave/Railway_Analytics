const express = require('express');
const oracledb = require('oracledb');
const cors = require('cors');
require('dotenv').config();
oracledb.initOracleClient({libDir: process.env.INSTANT_CLIENT});
const app = express();
app.use(cors());
app.use(express.json());

// Database configuration
const dbConfig = {
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  connectString: `${process.env.DB_HOST}:${process.env.DB_PORT}/${process.env.DB_SID}`
};

const TARGET_SCHEMA = "FOISGOODS";

// Years data
const years = ["25_26", "24_25", "23_24", "22_23", "21_22", "20_21", "19_20", "18_19", "17_18"];
const yearLabels = {
  "25_26": "2025-26",
  "24_25": "2024-25",
  "23_24": "2023-24",
  "22_23": "2022-23",
  "21_22": "2021-22",
  "20_21": "2020-21",
  "19_20": "2019-20",
  "18_19": "2018-19",
  "17_18": "2017-18"
};

// SQL queries
const queries = [
  "SELECT SUM(CHBL_WGHT) AS SUM_DIFF FROM {schema}.{table} WHERE ZONE_FRM = 'WR'",
  "SELECT SUM(TOT_FRT_INCL_GST - TOT_GST) AS SUM_DIFF FROM {schema}.{table} WHERE ZONE_FRM = 'WR'",
  "SELECT SUM(WR) AS SUM_DIFF FROM {schema}.{table} WHERE ZONE_FRM = 'WR'",
  "SELECT SUM(WR) AS SUM_DIFF FROM {schema}.{table} WHERE ZONE_FRM != 'WR'"
];

// Helper function to calculate percentage variance
const calculatePctVar = (current, previous) => {
  if (previous && previous !== 0) {
    return ((current - previous) / previous) * 100;
  }
  return null;
};

// API endpoint to get traffic data
app.get('/api/traffic-data', async (req, res) => {
  const { selectedYear } = req.query;
  
  try {
    // Get the index of the selected year
    const selectedIdx = Object.values(yearLabels).indexOf(selectedYear);
    // Get the 5 years (selected and previous 4)
    const tableYears = years.slice(selectedIdx, selectedIdx + 5);
    
    const connection = await oracledb.getConnection(dbConfig);
    
    const results = [];
    
    for (const year of tableYears) {
      const table = `carr_apmt_excl_adv_${year}`;
      const rowVals = [];
      
      for (const q of queries) {
        const result = await connection.execute(
          q.replace('{schema}', TARGET_SCHEMA).replace('{table}', table)
        );
        const val = result.rows[0][0] || 0;
        rowVals.push(val);
      }
      
      // Calculate derived values
      const [row3, row4] = [rowVals[2], rowVals[3]];
      const row5 = row3 + row4;
      const row2 = rowVals[1];
      
      const row6 = row2 ? row5 / row2 : null;
      const row7 = row2 ? row3 / row2 : null;
      const row8 = row5 ? row3 / row5 : null;
      const row9 = row5 ? row4 / row5 : null;
      
      // Convert to crore and percentages
      const rowValsCrore = [
        rowVals[0],
        row2,
        row3,
        row4,
        row5
      ];
      
      const derivedPercent = [
        row6 ? row6 * 100 : null,
        row7 ? row7 * 100 : null,
        row8 ? row8 * 100 : null,
        row9 ? row9 * 100 : null
      ];
      
      results.push({
        year: yearLabels[year],
        values: rowValsCrore,
        ratios: derivedPercent
      });
    }
    
    await connection.close();
    
    // Prepare summary data
    const summaryData = results.map(r => r.values);
    const summaryNames = [
      "Loading",
      "Originating Revenue",
      "Apportioned Revenue (Outward Retained Share)",
      "Apportioned Revenue (Inward Share)",
      "Total Apportioned Revenue (3+4)"
    ];
    
    const summaryRows = summaryNames.map((name, i) => {
      const rowData = {
        particular: name,
        values: summaryData.map(d => d[i])
      };
      
      // Calculate % variance
      if (summaryData.length >= 2) {
        const current = summaryData[0][i];
        const previous = summaryData[1][i];
        rowData.pctVar = calculatePctVar(current, previous);
      }
      
      return rowData;
    });
    
    // Prepare ratio data
    const ratioData = results.map(r => r.ratios);
    const ratioNames = [
      "Ratio of Apportioned to Originating Revenue (5/2)",
      "Ratio of Outward Retained Share to Originating Revenue (3/2)",
      "Ratio of Outward Retained Share to Total Apportioned Revenue (3/5)",
      "Ratio of Inward Share to Total Apportioned Revenue (4/5)"
    ];
    
    const ratioRows = ratioNames.map((name, i) => {
      const rowData = {
        ratio: name,
        values: ratioData.map(d => d[i])
      };
      
      // Calculate average of last 5 years
      const validValues = ratioData.map(d => d[i]).filter(v => v !== null);
      if (validValues.length > 0) {
        rowData.average = validValues.reduce((a, b) => a + b, 0) / validValues.length;
      }
      
      return rowData;
    });
    
    res.json({
      years: results.map(r => r.year),
      summary: summaryRows,
      ratios: ratioRows
    });
    
  } catch (error) {
    console.error('Error fetching data:', error);
    res.status(500).json({ error: 'Failed to fetch data' });
  }
});

// Add this to your server.js file
app.get('/api/chart-data', async (req, res) => {
  const { year, chartType } = req.query;
  
  try {
    const connection = await oracledb.getConnection(dbConfig);
    
    // Example query - you'll need to adjust this based on your actual data structure
    let query, results;
    
    if (chartType === 'line') {
      // Monthly performance data
      query = `SELECT month, value FROM ${TARGET_SCHEMA}.monthly_performance WHERE year = :year ORDER BY month_num`;
      results = await connection.execute(query, [year]);
      
      const lineData = results.rows.map(row => ({
        month: row[0],
        value: row[1]
      }));
      
      res.json({ line: lineData });
    } else if (chartType === 'bar') {
      // Product performance data
      query = `SELECT product_category, performance_value FROM ${TARGET_SCHEMA}.product_performance WHERE year = :year ORDER BY performance_value DESC`;
      results = await connection.execute(query, [year]);
      
      const barData = results.rows.map(row => ({
        category: row[0],
        value: row[1]
      }));
      
      res.json({ bar: barData });
    }
    
    await connection.close();
  } catch (error) {
    console.error('Error fetching chart data:', error);
    res.status(500).json({ error: 'Failed to fetch chart data' });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});