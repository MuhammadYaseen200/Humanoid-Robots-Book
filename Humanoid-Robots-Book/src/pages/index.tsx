import React from 'react';
import Layout from '@theme/Layout';
import HeroSection from '@site/src/components/LandingPage/HeroSection';
import FeatureGrid from '@site/src/components/LandingPage/FeatureGrid';

export default function Home(): JSX.Element {
  return (
    <Layout
      title="Master Physical AI & Humanoid Robotics"
      description="Free interactive textbook with AI-powered RAG chatbot for learning ROS 2, Isaac Sim, Gazebo, and humanoid robotics"
    >
      <HeroSection />
      <main>
        <FeatureGrid />
      </main>
    </Layout>
  );
}
