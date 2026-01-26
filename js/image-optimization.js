/**
 * 이미지 최적화 스크립트
 * - 모든 이미지에 lazy loading 추가
 * - alt 속성이 없는 이미지에 기본 alt 추가
 */

(function() {
  'use strict';

  // DOM이 로드된 후 실행
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    optimizeImages();
  }

  function optimizeImages() {
    // 포스트 컨테이너 내의 모든 이미지 선택
    const postContainer = document.querySelector('.post-container');
    if (!postContainer) return;

    const images = postContainer.querySelectorAll('img');
    
    images.forEach(function(img) {
      // lazy loading 추가 (이미 있는 경우 스킵)
      if (!img.hasAttribute('loading')) {
        img.setAttribute('loading', 'lazy');
      }

      // alt 속성이 없거나 빈 경우 기본값 추가
      if (!img.hasAttribute('alt') || img.getAttribute('alt') === '') {
        // 이미지 파일명에서 기본 alt 텍스트 생성
        const src = img.getAttribute('src') || '';
        const filename = src.split('/').pop().split('.')[0] || '이미지';
        img.setAttribute('alt', filename);
      }

      // decoding="async" 추가로 이미지 디코딩 최적화
      if (!img.hasAttribute('decoding')) {
        img.setAttribute('decoding', 'async');
      }
    });
  }
})();
