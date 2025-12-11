import React from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  Icon: React.ComponentType<React.ComponentProps<'svg'>>;
  description: React.JSX.Element;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'Comprehensive Physical AI Curriculum',
    Svg: require('@site/static/img/undraw_robotics_curriculum.svg').default,
    Icon: require('@site/static/img/ai-icon-curriculum.svg').default,
    description: (
      <>
        Master the fundamentals of Physical AI and humanoid robotics through our structured curriculum covering theory, locomotion, perception, control systems, and advanced applications.
      </>
    ),
  },
  {
    title: 'Practical Applications & Implementation',
    Svg: require('@site/static/img/undraw_practical_implementation.svg').default,
    Icon: require('@site/static/img/ai-icon-implementation.svg').default,
    description: (
      <>
        Learn through hands-on examples and real-world case studies that bridge the gap between theoretical concepts and practical implementation in robotics and AI systems.
      </>
    ),
  },
  {
    title: 'Cutting-Edge Research & Development',
    Svg: require('@site/static/img/undraw_research_development.svg').default,
    Icon: require('@site/static/img/ai-icon-research.svg').default,
    description: (
      <>
        Explore the latest advancements in humanoid robotics, embodied intelligence, and multi-robot systems with insights from current research and industry applications.
      </>
    ),
  },
];

function Feature({title, Svg, Icon, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4', styles.featureCardWrapper)}>
      <div className={styles.featureCard}>
        <div className={clsx('text--center', styles.featureHeader)}>
          <div className={styles.featureIconContainer}>
            <Icon className={styles.featureIcon} />
          </div>
        </div>
        <div className="text--center">
          <Heading as="h3" className={styles.featureTitle}>
            {title}
          </Heading>
          <p className={styles.featureDescription}>
            {description}
          </p>
        </div>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): React.JSX.Element {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
