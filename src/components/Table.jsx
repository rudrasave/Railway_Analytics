import * as React from 'react';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';

const summaryColumns = [
  { id: 'srNo', label: 'Sr.No', minWidth: 50, align: 'center' },
  { id: 'particulars', label: 'Particulars', minWidth: 300 },
];

const ratioColumns = [
  { id: 'srNo', label: 'Sr.No', minWidth: 50, align: 'center' },
  { id: 'ratio', label: 'Ratio', minWidth: 300 },
];

const fiscalYears = [
  '2025-26',
  '2024-25',
  '2023-24',
  '2022-23',
  '2021-22',
  '2020-21',
  '2019-20',
  '2018-19',
  '2017-18'
];

export default function DataTable() {
  const [selectedYear, setSelectedYear] = React.useState('2023-24');
  const [tableData, setTableData] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const fetchData = async (year) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/api/traffic-data?selectedYear=${year}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setTableData(data);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    fetchData(selectedYear);
  }, [selectedYear]);

  const handleYearChange = (event) => {
    setSelectedYear(event.target.value);
  };

  const getLastFiveYears = () => {
    if (!tableData) return [];
    const selectedIndex = tableData.years.indexOf(selectedYear);
    const startIndex = Math.max(0, selectedIndex - 4);
    return tableData.years.slice(startIndex, selectedIndex + 1);
  };

  const transformSummaryData = () => {
    if (!tableData) return [];
    
    const yearsToShow = getLastFiveYears();
    
    return tableData.summary.slice(0, 5).map((row, index) => {
      const values = {};
      const percentageChanges = {};
      
      yearsToShow.forEach((year, i) => {
        const yearIndex = tableData.years.indexOf(year);
        values[year] = row.values[yearIndex];
        
        // Calculate percentage change from previous year
        if (i > 0) {
          const prevYear = yearsToShow[i-1];
          const prevYearIndex = tableData.years.indexOf(prevYear);
          const prevValue = row.values[prevYearIndex];
          const currentValue = row.values[yearIndex];
          
          if (prevValue !== 0) {
            percentageChanges[year] = ((currentValue - prevValue) / prevValue) * 100;
          } else {
            percentageChanges[year] = null;
          }
        } else {
          percentageChanges[year] = null;
        }
      });
      
      return {
        srNo: index + 1,
        particulars: row.particular,
        values: values,
        percentageChanges: percentageChanges
      };
    });
  };

  const transformRatioData = () => {
    if (!tableData) return [];
    
    const yearsToShow = getLastFiveYears();
    
    return tableData.ratios.map((row, index) => {
      const values = {};
      let sum = 0;
      let count = 0;
      
      yearsToShow.forEach(year => {
        const yearIndex = tableData.years.indexOf(year);
        values[year] = row.values[yearIndex];
        
        if (row.values[yearIndex] !== null) {
          sum += row.values[yearIndex];
          count++;
        }
      });
      
      const average = count > 0 ? sum / count : null;
      
      return {
        srNo: index + 1,
        ratio: row.ratio,
        values: values,
        average: average
      };
    });
  };

  const summaryRows = transformSummaryData();
  const ratioRows = transformRatioData();
  const yearsToShow = tableData ? getLastFiveYears() : [];

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden', padding: 2 }}>
      <FormControl sx={{ minWidth: 120, marginBottom: 2 }}>
        <InputLabel id="year-select-label">Fiscal Year</InputLabel>
        <Select
          labelId="year-select-label"
          id="year-select"
          value={selectedYear}
          label="Fiscal Year"
          onChange={handleYearChange}
          disabled={loading}
        >
          {fiscalYears.map((year) => (
            <MenuItem key={year} value={year}>
              {year}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error loading data: {error}
        </Alert>
      )}

      {!loading && !error && tableData && (
        <>
          {/* Summary Table */}
          <Box sx={{ mb: 4 }}>
            <TableContainer sx={{ maxHeight: 440 }}>
              <Table stickyHeader aria-label="summary table">
                <TableHead>
                  <TableRow>
                    {summaryColumns.map((column) => (
                      <TableCell
                        key={column.id}
                        align={column.align}
                        style={{ 
                          minWidth: column.minWidth, 
                          backgroundColor: '#e0e0e0', 
                          fontWeight: 'bold' 
                        }}
                      >
                        {column.label}
                      </TableCell>
                    ))}
                    {yearsToShow.map((year) => [
                      <TableCell
                        key={`${year}-value`}
                        align="right"
                        style={{ 
                          minWidth: 100, 
                          backgroundColor: '#e0e0e0', 
                          fontWeight: 'bold' 
                        }}
                      >
                        {year} (Value)
                      </TableCell>,
                      <TableCell
                        key={`${year}-pct`}
                        align="right"
                        style={{ 
                          minWidth: 120, 
                          backgroundColor: '#e0e0e0', 
                          fontWeight: 'bold' 
                        }}
                      >
                        {year} (% Var)
                      </TableCell>
                    ])}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {summaryRows.map((row) => (
                    <TableRow hover role="checkbox" tabIndex={-1} key={row.srNo}>
                      <TableCell align="center">{row.srNo}</TableCell>
                      <TableCell>{row.particulars}</TableCell>
                      {yearsToShow.map((year) => [
                        <TableCell key={`${year}-val`} align="right">
                          {typeof row.values[year] === 'number' 
                            ? row.values[year].toLocaleString('en-US') 
                            : 'N/A'}
                        </TableCell>,
                        <TableCell key={`${year}-pct`} align="right">
                          {row.percentageChanges[year] !== null 
                            ? `${row.percentageChanges[year]?.toFixed(2)}%` 
                            : 'N/A'}
                        </TableCell>
                      ])}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>

          {/* Ratios Table */}
          <Box sx={{ mt: 4 }}>
            <TableContainer sx={{ maxHeight: 440 }}>
              <Table stickyHeader aria-label="ratio table">
                <TableHead>
                  <TableRow>
                    {ratioColumns.map((column) => (
                      <TableCell
                        key={column.id}
                        align={column.align}
                        style={{ 
                          minWidth: column.minWidth, 
                          backgroundColor: '#e0e0e0', 
                          fontWeight: 'bold' 
                        }}
                      >
                        {column.label}
                      </TableCell>
                    ))}
                    {yearsToShow.map((year) => (
                      <TableCell
                        key={year}
                        align="right"
                        style={{ 
                          minWidth: 100, 
                          backgroundColor: '#e0e0e0', 
                          fontWeight: 'bold' 
                        }}
                      >
                        {year}
                      </TableCell>
                    ))}
                    <TableCell
                      align="right"
                      style={{ 
                        minWidth: 120, 
                        backgroundColor: '#e0e0e0', 
                        fontWeight: 'bold' 
                      }}
                    >
                      5-Year Avg
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {ratioRows.map((row) => (
                    <TableRow hover role="checkbox" tabIndex={-1} key={row.srNo}>
                      <TableCell align="center">{row.srNo}</TableCell>
                      <TableCell>{row.ratio}</TableCell>
                      {yearsToShow.map((year) => (
                        <TableCell key={year} align="right">
                          {typeof row.values[year] === 'number' 
                            ? row.values[year].toFixed(2)
                            : 'N/A'}
                        </TableCell>
                      ))}
                      <TableCell align="right">
                        {row.average !== null 
                          ? row.average.toFixed(2)
                          : 'N/A'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        </>
      )}
    </Paper>
  );
}