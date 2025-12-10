import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  textbookSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Physical AI Fundamentals',
      items: [
        'physical-ai-fundamentals',
      ],
    },
    {
      type: 'category',
      label: 'Robotics Foundations',
      items: [
        'robotics-fundamentals-kinematics',
        'sensor-systems-perception',
        'control-theory-physical-ai',
      ],
    },
    {
      type: 'category',
      label: 'Locomotion and Manipulation',
      items: [
        'locomotion-mobility',
        'manipulation-grasping',
      ],
    },
    {
      type: 'category',
      label: 'Human-Robot Interaction',
      items: [
        'human-robot-interaction',
      ],
    },
    {
      type: 'category',
      label: 'Learning and Adaptation',
      items: [
        'learning-physical-systems',
      ],
    },
    {
      type: 'category',
      label: 'Safety and Ethics',
      items: [
        'safety-ethics-physical-ai',
      ],
    },
    {
      type: 'category',
      label: 'Multi-Robot Systems',
      items: [
        'multi-robot-systems',
      ],
    },
    {
      type: 'category',
      label: 'Embodied Intelligence',
      items: [
        'embodied-ai-cognition',
      ],
    },
    {
      type: 'category',
      label: 'Hardware Design',
      items: [
        'hardware-design-humanoid-robots',
      ],
    },
    {
      type: 'category',
      label: 'Simulation and Transfer',
      items: [
        'simulation-real-world-transfer',
      ],
    },
    {
      type: 'category',
      label: 'Energy and Efficiency',
      items: [
        'energy-management-efficiency',
      ],
    },
    {
      type: 'category',
      label: 'Advanced Control',
      items: [
        'advanced-control-strategies',
      ],
    },
    {
      type: 'category',
      label: 'Applications and Case Studies',
      items: [
        'applications-case-studies',
      ],
    },
    {
      type: 'category',
      label: 'Future Directions',
      items: [
        'future-directions-physical-ai',
      ],
    },
    {
      type: 'category',
      label: 'System Development',
      items: [
        'troubleshooting-debugging',
        'performance-optimization',
        'integration-system-design',
      ],
    },
  ],

  // But you can create a sidebar manually
  /*
  tutorialSidebar: [
    'intro',
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
   */
};

export default sidebars;
