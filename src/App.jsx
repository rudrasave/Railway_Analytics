import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './Home';
import About from './About';
import Dashboard from './Dashboard';
import Login from './Auth/Login';
import Signup from './Auth/Signin';
import PrivateRoute from './components/PrivateRoute';
import Page1 from './components/Page1';
import Display from './components/Display';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected Routes */}
        <Route path="/about" element={<PrivateRoute><About /></PrivateRoute>} />
        
        {/* Dashboard with Sidebar */}
        <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>}>
          <Route index element={<Page1 />} /> {/* Default to Page1 */}
          <Route path="page1" element={<Page1 />} />
          <Route path="display" element={<Display />} />
        </Route>
        
        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;