/**
 * Lazy Loading Hook
 * TASK-044: Implement lazy loading for large lists
 */

import { useState, useEffect, useRef, useCallback } from 'react';

interface UseLazyLoadOptions {
  threshold?: number;
  rootMargin?: string;
  enabled?: boolean;
}

export const useLazyLoad = <T extends HTMLElement>(
  onLoadMore: () => void,
  options: UseLazyLoadOptions = {}
) => {
  const { threshold = 0.1, rootMargin = '100px', enabled = true } = options;
  const [isLoading, setIsLoading] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const elementRef = useRef<T | null>(null);

  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      if (entry.isIntersecting && enabled && !isLoading) {
        setIsLoading(true);
        onLoadMore();
      }
    },
    [onLoadMore, enabled, isLoading]
  );

  useEffect(() => {
    if (!enabled || !elementRef.current) return;

    observerRef.current = new IntersectionObserver(handleIntersection, {
      threshold,
      rootMargin,
    });

    const currentElement = elementRef.current;
    observerRef.current.observe(currentElement);

    return () => {
      if (observerRef.current && currentElement) {
        observerRef.current.unobserve(currentElement);
      }
    };
  }, [handleIntersection, threshold, rootMargin, enabled]);

  const setElement = useCallback((element: T | null) => {
    if (observerRef.current && elementRef.current) {
      observerRef.current.unobserve(elementRef.current);
    }

    elementRef.current = element;

    if (element && observerRef.current) {
      observerRef.current.observe(element);
    }
  }, []);

  const finishLoading = useCallback(() => {
    setIsLoading(false);
  }, []);

  return {
    elementRef: setElement,
    isLoading,
    finishLoading,
  };
};

