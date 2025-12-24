import React from 'react';
import Link from '@docusaurus/Link';
import { useAuth } from '@site/src/context/AuthContext'; // Feature 003 integration

export default function HeroSection() {
  // Check authentication state from Feature 003-better-auth
  const { user } = useAuth();

  return (
    <section className="hero hero--primary">
      <div className="container">
        <div className="row">
          <div className="col col--12">
            <h1 className="hero__title">
              Master Physical AI & Humanoid Robotics
            </h1>
            <p className="hero__subtitle">
              A free, interactive textbook with an AI-powered RAG chatbot for learning ROS 2,
              Isaac Sim, Gazebo, and humanoid robotics. Designed for students and self-taught
              developers to build real-world Physical AI systems from simulation to deployment.
            </p>
            <div className="buttons">
              <Link
                className="button button--secondary button--lg"
                to="/docs/module-1-ros2-basics/chapter-1-intro"
              >
                {user ? 'Continue Learning' : 'Get Started'}
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
