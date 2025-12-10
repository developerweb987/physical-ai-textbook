import React, { useState, useEffect } from 'react';
import { useLocation, Link } from '@docusaurus/router';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import './ChapterNavigation.css';

const ChapterNavigation = () => {
  const location = useLocation();
  const { siteConfig } = useDocusaurusContext();
  const [chapters, setChapters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For now, we'll create a static list of chapters
  // In a real implementation, this would come from an API
  const staticChapters = [
    {
      id: 1,
      title: 'Introduction to Physical AI & Humanoid Robotics',
      slug: 'intro',
      chapterNumber: 1,
      learningOutcomes: [
        'Understand the principles of Physical AI',
        'Analyze the components of humanoid robotics'
      ],
      status: 'published',
      progress: 0
    },
    {
      id: 2,
      title: 'Physical AI Fundamentals',
      slug: 'physical-ai-fundamentals',
      chapterNumber: 2,
      learningOutcomes: [
        'Define Physical AI and distinguish it from traditional AI',
        'Explain the key challenges in Physical AI systems'
      ],
      status: 'published',
      progress: 0
    },
    {
      id: 3,
      title: 'Mechanical Systems in Humanoid Robots',
      slug: 'mechanical-systems',
      chapterNumber: 3,
      learningOutcomes: [
        'Analyze the mechanical design of humanoid robots',
        'Evaluate different actuation systems'
      ],
      status: 'draft',
      progress: 0
    },
    {
      id: 4,
      title: 'Sensors and Perception',
      slug: 'sensors-perception',
      chapterNumber: 4,
      learningOutcomes: [
        'Identify different types of sensors used in humanoid robots',
        'Explain sensor fusion techniques'
      ],
      status: 'draft',
      progress: 0
    }
  ];

  useEffect(() => {
    // Simulate API call to get chapters
    const fetchChapters = async () => {
      try {
        // In a real implementation, this would be an API call:
        // const response = await fetch('/api/v1/chapters?status=published');
        // const data = await response.json();
        // setChapters(data);

        // For now, use static data
        setChapters(staticChapters);
        setLoading(false);
      } catch (err) {
        setError('Failed to load chapters');
        setLoading(false);
        console.error('Error loading chapters:', err);
      }
    };

    fetchChapters();
  }, []);

  if (loading) {
    return <div className="chapter-navigation-loading">Loading chapters...</div>;
  }

  if (error) {
    return <div className="chapter-navigation-error">Error: {error}</div>;
  }

  // Find current chapter based on URL
  const currentPath = location.pathname;
  const currentChapter = chapters.find(chapter =>
    currentPath.includes(chapter.slug) ||
    (chapter.chapterNumber === 1 && currentPath.endsWith('/'))
  );

  // Find next and previous chapters
  const currentChapterIndex = chapters.findIndex(ch => ch.id === currentChapter?.id);
  const prevChapter = currentChapterIndex > 0 ? chapters[currentChapterIndex - 1] : null;
  const nextChapter = currentChapterIndex < chapters.length - 1 ? chapters[currentChapterIndex + 1] : null;

  return (
    <div className="chapter-navigation-container">
      <div className="chapter-list">
        <h3>Table of Contents</h3>
        <ul>
          {chapters
            .filter(chapter => chapter.status === 'published')
            .map((chapter) => (
              <li
                key={chapter.id}
                className={`chapter-item ${currentChapter?.id === chapter.id ? 'current-chapter' : ''}`}
              >
                <Link
                  to={`/docs/${chapter.slug}`}
                  className={`chapter-link ${currentChapter?.id === chapter.id ? 'current' : ''}`}
                >
                  <span className="chapter-number">{chapter.chapterNumber}.</span>
                  <span className="chapter-title">{chapter.title}</span>
                  {chapter.progress > 0 && (
                    <span className="chapter-progress">{Math.round(chapter.progress)}%</span>
                  )}
                </Link>
              </li>
            ))}
        </ul>
      </div>

      {currentChapter && (location.pathname.includes('/docs/') || location.pathname.endsWith('/')) && (
        <div className="chapter-navigation-links">
          <div className="navigation-buttons">
            {prevChapter ? (
              <Link to={`/docs/${prevChapter.slug}`} className="nav-button prev-button">
                ← Previous: {prevChapter.title}
              </Link>
            ) : (
              <div className="nav-button prev-button disabled">← Previous</div>
            )}

            {nextChapter ? (
              <Link to={`/docs/${nextChapter.slug}`} className="nav-button next-button">
                Next: {nextChapter.title} →
              </Link>
            ) : (
              <div className="nav-button next-button disabled">Next →</div>
            )}
          </div>

          <div className="chapter-learning-outcomes">
            <h4>Learning Outcomes</h4>
            <ul>
              {currentChapter.learningOutcomes.map((outcome, index) => (
                <li key={index} className="learning-outcome">
                  {outcome}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChapterNavigation;