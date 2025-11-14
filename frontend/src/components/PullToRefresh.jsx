import React, { useState, useRef, useEffect } from 'react';
import { RefreshCw } from 'lucide-react';

const PullToRefresh = ({ onRefresh, children }) => {
  const [pulling, setPulling] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const [refreshing, setRefreshing] = useState(false);
  const startY = useRef(0);
  const containerRef = useRef(null);

  const PULL_THRESHOLD = 80;
  const MAX_PULL = 120;

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    let touchStartY = 0;
    let currentY = 0;

    const handleTouchStart = (e) => {
      // Only start pulling if we're at the top of the scroll
      if (container.scrollTop === 0 && !refreshing) {
        touchStartY = e.touches[0].clientY;
        startY.current = touchStartY;
      }
    };

    const handleTouchMove = (e) => {
      if (refreshing || !startY.current) return;

      currentY = e.touches[0].clientY;
      const distance = currentY - startY.current;

      // Only pull down when at the top
      if (distance > 0 && container.scrollTop === 0) {
        e.preventDefault();
        setPulling(true);

        // Apply resistance curve
        const adjustedDistance = Math.min(
          distance * 0.5,
          MAX_PULL
        );

        setPullDistance(adjustedDistance);
      }
    };

    const handleTouchEnd = async () => {
      if (refreshing) return;

      if (pullDistance >= PULL_THRESHOLD) {
        setRefreshing(true);
        setPullDistance(PULL_THRESHOLD);

        try {
          await onRefresh();
        } catch (error) {
          console.error('Refresh error:', error);
        } finally {
          setTimeout(() => {
            setRefreshing(false);
            setPullDistance(0);
            setPulling(false);
          }, 500);
        }
      } else {
        // Reset
        setPullDistance(0);
        setPulling(false);
      }

      startY.current = 0;
    };

    container.addEventListener('touchstart', handleTouchStart, { passive: true });
    container.addEventListener('touchmove', handleTouchMove, { passive: false });
    container.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
    };
  }, [pullDistance, refreshing, onRefresh]);

  const rotation = pulling ? (pullDistance / PULL_THRESHOLD) * 360 : 0;
  const opacity = Math.min(pullDistance / PULL_THRESHOLD, 1);

  return (
    <div ref={containerRef} className="h-full overflow-auto">
      {/* Pull to refresh indicator */}
      <div
        className="pull-to-refresh"
        style={{
          transform: `translateY(${pullDistance - 100}%)`,
          opacity: opacity,
        }}
      >
        <RefreshCw
          size={24}
          className="text-primary-600"
          style={{
            transform: `rotate(${rotation}deg)`,
            transition: refreshing ? 'transform 0.5s linear' : 'none',
            animation: refreshing ? 'spin 1s linear infinite' : 'none',
          }}
        />
        <span className="text-sm text-gray-600 ml-2">
          {refreshing ? 'Odświeżanie...' : pullDistance >= PULL_THRESHOLD ? 'Puść aby odświeżyć' : 'Przeciągnij aby odświeżyć'}
        </span>
      </div>

      {children}
    </div>
  );
};

export default PullToRefresh;
