// Dashboard.jsx
import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import './Dashboard.css';

const Dashboard = () => {
  return (
    <div className="dashboard-container">
      <Sidebar />
      <div className="dashboard-content">
        <Outlet />
      </div>
    </div>
  );
};

export default Dashboard;