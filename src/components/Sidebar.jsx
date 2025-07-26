import React from 'react';
import { NavLink } from 'react-router-dom';
import './Sidebar.css';

const Sidebar = () => (
  <aside className="sidebar">
    <nav className="sidebar-nav">
      <NavLink 
        to="page1"
        className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}
      >
        <span className="material-icons-outlined">insights</span>
        <span>Analytics</span>
      </NavLink>
      <NavLink 
        to="display"
        className={({ isActive }) => isActive ? 'sidebar-link active' : 'sidebar-link'}
      >
        <span className="material-icons-outlined">dashboard</span>
        <span>Display</span>
      </NavLink>
      <div className="sidebar-footer">
        <div className="user-profile">
          <div className="avatar">JS</div>
          <div className="user-info">
            <div className="username">John Smith</div>
            <div className="user-role">Admin</div>
          </div>
        </div>
      </div>
    </nav>
  </aside>
);

export default Sidebar;