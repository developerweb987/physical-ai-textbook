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
    {
      type: 'category',
      label: 'Module 01: Introduction',
      collapsible: true,
      collapsed: false,
      items: [
        'introduction/index',
        'introduction/intro',
      ],
    },
    {
      type: 'category',
      label: 'Module 02: Theory & Fundamentals',
      collapsible: true,
      collapsed: true,
      items: [
        'theory-fundamentals/index',
        'theory-fundamentals/physical-ai-fundamentals',
        'theory-fundamentals/robotics-fundamentals-kinematics',
      ],
    },
    {
      type: 'category',
      label: 'Module 03: Locomotion & Manipulation',
      collapsible: true,
      collapsed: true,
      items: [
        'locomotion-manipulation/index',
        'locomotion-manipulation/locomotion-mobility',
        'locomotion-manipulation/manipulation-grasping',
      ],
    },
    {
      type: 'category',
      label: 'Module 04: Perception & Control',
      collapsible: true,
      collapsed: true,
      items: [
        'perception-control/index',
        'perception-control/sensor-systems-perception',
        'perception-control/control-theory-physical-ai',
      ],
    },
    {
      type: 'category',
      label: 'Module 05: Advanced Topics',
      collapsible: true,
      collapsed: true,
      items: [
        'advanced-topics/index',
        'advanced-topics/human-robot-interaction',
        'advanced-topics/learning-physical-systems',
        'advanced-topics/safety-ethics-physical-ai',
        'advanced-topics/multi-robot-systems',
        'advanced-topics/embodied-ai-cognition',
      ],
    },
    {
      type: 'category',
      label: 'Module 06: Applications & Implementation',
      collapsible: true,
      collapsed: true,
      items: [
        'applications-implementation/index',
        'applications-implementation/hardware-design-humanoid-robots',
        'applications-implementation/simulation-real-world-transfer',
        'applications-implementation/energy-management-efficiency',
        'applications-implementation/advanced-control-strategies',
        'applications-implementation/applications-case-studies',
        'applications-implementation/future-directions-physical-ai',
      ],
    },
    {
      type: 'category',
      label: 'References & Resources',
      collapsible: true,
      collapsed: true,
      items: [
        'references/index',
        'references/troubleshooting-debugging',
        'references/performance-optimization',
        'references/integration-system-design',
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
