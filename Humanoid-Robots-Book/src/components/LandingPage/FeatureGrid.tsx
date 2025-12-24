import React from 'react';
import { MessageSquare, Cpu, Languages, Rocket } from 'lucide-react';

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

function FeatureCard({ icon, title, description }: FeatureCardProps) {
  return (
    <div className="col col--3">
      <div className="text--center padding-horiz--md">
        <div style={{ fontSize: '48px', marginBottom: '1rem' }}>
          {icon}
        </div>
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function FeatureGrid() {
  const features: FeatureCardProps[] = [
    {
      icon: <MessageSquare size={48} className="text-blue-500" />,
      title: 'Interactive RAG Chatbot',
      description:
        'Ask questions about any chapter and get instant answers with citations. Powered by AI for contextual learning.',
    },
    {
      icon: <Cpu size={48} className="text-green-500" />,
      title: 'Hardware-Aware Learning',
      description:
        'Content adapts to your GPU and experience level. Get tailored recommendations for local vs. cloud workflows.',
    },
    {
      icon: <Languages size={48} className="text-purple-500" />,
      title: 'Urdu Translation',
      description:
        'Toggle between English and Urdu for accessible learning. Roman Urdu support for Pakistani students.',
    },
    {
      icon: <Rocket size={48} className="text-orange-500" />,
      title: 'Real-World Projects',
      description:
        'Build actual humanoid robots with ROS 2 and Isaac Sim. From simulation to deployment on NVIDIA Jetson.',
    },
  ];

  return (
    <section className="features">
      <div className="container">
        <div className="row">
          {features.map((feature, idx) => (
            <FeatureCard key={idx} {...feature} />
          ))}
        </div>
      </div>
    </section>
  );
}
