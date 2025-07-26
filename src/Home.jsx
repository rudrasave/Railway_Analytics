import React from 'react';
import './Home.css';

function Home() {
  return (
    <div className="home-container">
      <section className="hero">
        <h1>RailAnalytics</h1>
        <p className="subtitle">Smarter Railways. Powerful Insights.</p>
        <a href="/dashboard" className="cta-button">Explore Dashboard</a>
      </section>
      <section className="features">
        <div className="feature-card">
          <h2>Live Data</h2>
          <p>Access real-time analytics for informed, agile decisions.</p>
        </div>
        <div className="feature-card">
          <h2>Insightful Reports</h2>
          <p>Visualize trends and performance with beautiful, clear reports.</p>
        </div>
        <div className="feature-card">
          <h2>Intuitive Design</h2>
          <p>Navigate with ease using our clean, user-focused interface.</p>
        </div>
      </section>
    </div>
  );
}

export default Home; 