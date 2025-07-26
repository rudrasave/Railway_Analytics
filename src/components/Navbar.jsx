import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import './Navbar.css';
import { useAuthState } from 'react-firebase-hooks/auth';
import { auth } from '../Auth/firebase';
import { Button } from '@mui/material';

function Navbar() {
  const [user] = useAuthState(auth);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await auth.signOut();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-brand">
          <span className="navbar-logo">R</span>
          RailAnalytics
        </NavLink>
        <div className="navbar-links">
          <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} end>Home</NavLink>
          <NavLink to="/about" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>About</NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Dashboard</NavLink>
          {!user && <NavLink to="/login" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Login</NavLink>}
          {!user && <NavLink to="/signup" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>Signin</NavLink>}
          {user && <Button variant="outlined" color="inherit" size="small" onClick={handleLogout} sx={{ ml: 2 }}>Logout</Button>}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;