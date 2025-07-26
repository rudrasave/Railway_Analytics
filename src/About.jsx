import React from 'react';
import './About.css';

function About() {
  return (
    <div className="about-container">
      <section className="about-hero">
        <h1>About RailAnalytics</h1>
        <p className="about-subtitle">Empowering railways with clarity and innovation.</p>
      </section>
      <section className="about-content">
        <div className="about-story">
          <h2>Our Story</h2>
          <p>RailAnalytics was founded to bring clarity and efficiency to rail operations. Our team blends engineering and data science to deliver actionable insights for a safer, smarter railway future.</p>
        </div>
        <div className="about-mission">
          <h2>Our Mission</h2>
          <p>To enable railways to thrive through data-driven decisions, operational excellence, and sustainable growth.</p>
        </div>
        <div className="about-team">
          <h2>Meet the Team</h2>
          <ul>
            <li>Elvis Dsouza – Founder & CEO</li>
            <li>Jane Smith – Lead Data Scientist</li>
            <li>John Doe – Head of Engineering</li>
          </ul>
        </div>
      </section>
    </div>
  );
}

export default About; 