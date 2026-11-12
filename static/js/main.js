/**
 * VITHAIGAL IYAKKAM - MODERN DIGITAL PUBLISHING PLATFORM
 * Pure Vanilla JavaScript: Interactive Breaking News Slider,
 * Audio Reader, Font Resizer, Lightbox, Filter Tabs, Back-to-Top,
 * Live Search Dropdown, Theme Switcher & Bookmarks.
 */

document.addEventListener('DOMContentLoaded', () => {
  initLiveClock();
  initThemeToggle();
  initMobileDrawer();
  initBreakingNewsSlider();
  initScrollProgressBar();
  initBackToTop();
  initInteractiveFilterTabs();
  initArticleToolbar();
  initImageLightbox();
  initVideoLightbox();
  initLiveSearch();
  initBookmarks();
  initAjaxNewsletter();
  initCopyLinkButtons();
});

/* ==========================================================================
   1. LIVE CLOCK (Top Bar Real-time Clock)
   ========================================================================== */
function initLiveClock() {
  const clockEl = document.getElementById('live-clock');
  if (!clockEl) return;

  function update() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    clockEl.textContent = `${hours}:${minutes}:${seconds} ${ampm}`;
  }
  update();
  setInterval(update, 1000);
}

/* ==========================================================================
   2. THEME SWITCHER (Dark / Light Mode with Persistence)
   ========================================================================== */
function initThemeToggle() {
  const toggleBtns = document.querySelectorAll('.theme-toggle-btn');
  const savedTheme = localStorage.getItem('vi_theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcons(savedTheme);

  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme');
      const nextTheme = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', nextTheme);
      localStorage.setItem('vi_theme', nextTheme);
      updateThemeIcons(nextTheme);
      showToast(`Switched to ${nextTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
    });
  });

  function updateThemeIcons(theme) {
    toggleBtns.forEach(btn => {
      const icon = btn.querySelector('i');
      if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
      }
    });
  }
}

/* ==========================================================================
   3. MOBILE NAVIGATION DRAWER
   ========================================================================== */
function initMobileDrawer() {
  const toggleBtn = document.querySelector('.mobile-nav-toggle');
  const overlay = document.querySelector('.mobile-drawer-overlay');
  const closeBtn = document.querySelector('.drawer-close-btn');

  if (!toggleBtn || !overlay) return;

  toggleBtn.addEventListener('click', () => overlay.classList.add('active'));
  if (closeBtn) {
    closeBtn.addEventListener('click', () => overlay.classList.remove('active'));
  }
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.classList.remove('active');
  });
}

/* ==========================================================================
   4. POLIMER NEWS STYLE LIVE TV BREAKING NEWS BROADCAST SLIDER
   ========================================================================== */
function initBreakingNewsSlider() {
  const viewport = document.getElementById('polimer-slider-viewport') || document.getElementById('home-breaking-viewport');
  const track = document.getElementById('polimer-slider-track') || document.getElementById('home-breaking-track');
  const btnPrev = document.getElementById('polimer-slide-prev') || document.getElementById('breaking-slide-prev');
  const btnNext = document.getElementById('polimer-slide-next') || document.getElementById('breaking-slide-next');
  const counterEl = document.getElementById('polimer-counter');
  const dotsContainer = document.getElementById('polimer-slide-dots');

  if (!viewport || !track) return;

  const slides = Array.from(track.querySelectorAll('.polimer-slide-item, .breaking-insta-card'));
  const totalSlides = slides.length;
  if (totalSlides === 0) return;

  let currentSlide = 0;
  let autoplayTimer = null;
  const slideInterval = 4500; // 4.5 seconds per live breaking story
  let isHovered = false;

  // Real-time live clock updater for Polimer TV clock capsule
  function updateLiveClocks() {
    const clockEls = document.querySelectorAll('.polimer-live-clock');
    if (!clockEls.length) return;
    const now = new Date();
    let hours = now.getHours();
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    const timeStr = `${hours}:${minutes} ${ampm}`;
    clockEls.forEach((el) => {
      el.textContent = timeStr;
    });
  }
  updateLiveClocks();
  setInterval(updateLiveClocks, 1000);

  // Update slide position
  function goToSlide(index) {
    currentSlide = (index + totalSlides) % totalSlides;
    const slideWidth = viewport.getBoundingClientRect().width || viewport.clientWidth;
    track.style.transform = `translate3d(-${currentSlide * slideWidth}px, 0, 0)`;

    // Update Counter
    if (counterEl) {
      counterEl.textContent = `${currentSlide + 1} / ${totalSlides}`;
    }

    // Update Dots
    if (dotsContainer) {
      const dots = dotsContainer.querySelectorAll('.polimer-dot-btn');
      dots.forEach((dot, idx) => {
        if (idx === currentSlide) {
          dot.classList.add('active');
        } else {
          dot.classList.remove('active');
        }
      });
    }
  }

  function nextSlide() {
    goToSlide(currentSlide + 1);
  }

  function prevSlide() {
    goToSlide(currentSlide - 1);
  }

  // Autoplay engine
  function startAutoplay() {
    stopAutoplay();
    autoplayTimer = setInterval(() => {
      if (!isHovered) {
        nextSlide();
      }
    }, slideInterval);
  }

  function stopAutoplay() {
    if (autoplayTimer) {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  }

  // Hover to pause so user can comfortably read the TV quote & watch footage
  const broadcastCard = viewport.closest('.polimer-broadcast-card') || viewport;
  broadcastCard.addEventListener('mouseenter', () => {
    isHovered = true;
  });

  broadcastCard.addEventListener('mouseleave', () => {
    isHovered = false;
  });

  // Chevrons
  if (btnNext) {
    btnNext.addEventListener('click', (e) => {
      e.preventDefault();
      nextSlide();
      startAutoplay();
    });
  }

  if (btnPrev) {
    btnPrev.addEventListener('click', (e) => {
      e.preventDefault();
      prevSlide();
      startAutoplay();
    });
  }

  // Dots
  if (dotsContainer) {
    dotsContainer.addEventListener('click', (e) => {
      const dot = e.target.closest('.polimer-dot-btn');
      if (!dot) return;
      const targetIdx = parseInt(dot.getAttribute('data-index'), 10);
      if (!isNaN(targetIdx)) {
        goToSlide(targetIdx);
        startAutoplay();
      }
    });
  }

  // Mobile Touch Swipe
  let touchStartX = 0;
  let touchEndX = 0;

  viewport.addEventListener('touchstart', (e) => {
    isHovered = true;
    touchStartX = e.touches[0].clientX;
    touchEndX = touchStartX;
  }, { passive: true });

  viewport.addEventListener('touchmove', (e) => {
    touchEndX = e.touches[0].clientX;
  }, { passive: true });

  viewport.addEventListener('touchend', () => {
    const diff = touchStartX - touchEndX;
    if (Math.abs(diff) > 40) {
      if (diff > 0) {
        nextSlide();
      } else {
        prevSlide();
      }
    }
    isHovered = false;
    startAutoplay();
    touchStartX = 0;
    touchEndX = 0;
  });

  // Responsive recalculation on resize / orientation change
  window.addEventListener('resize', () => {
    goToSlide(currentSlide);
  });
  window.addEventListener('orientationchange', () => {
    setTimeout(() => goToSlide(currentSlide), 150);
  });

  // Launch initial slide and start continuous autoplay
  goToSlide(0);
  startAutoplay();
}

/* ==========================================================================
   5. SCROLL PROGRESS BAR (Window Top Reading Indicator)
   ========================================================================== */
function initScrollProgressBar() {
  const bar = document.getElementById('scroll-progress-indicator');
  if (!bar) return;

  window.addEventListener('scroll', () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
    bar.style.width = `${scrolled}%`;
  }, { passive: true });
}

/* ==========================================================================
   6. BACK TO TOP BUTTON (Interactive Floating Circular Button)
   ========================================================================== */
function initBackToTop() {
  const btn = document.getElementById('back-to-top-btn');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 280) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }, { passive: true });

  btn.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });
}

/* ==========================================================================
   7. INTERACTIVE HOMEPAGE CATEGORY FILTER TABS
   ========================================================================== */
function initInteractiveFilterTabs() {
  const tabBtns = document.querySelectorAll('.filter-tab-btn');
  const cards = document.querySelectorAll('.filterable-card');

  if (tabBtns.length === 0 || cards.length === 0) return;

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.getAttribute('data-filter');

      cards.forEach(card => {
        const cat = card.getAttribute('data-category');
        if (filter === 'all' || cat === filter) {
          card.classList.remove('hidden');
          card.classList.remove('fade-in');
          void card.offsetWidth; // trigger reflow
          card.classList.add('fade-in');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });
}

/* ==========================================================================
   8. INTERACTIVE ARTICLE TOOLBAR (Audio Reader, Font Resizer, Likes)
   ========================================================================== */
function initArticleToolbar() {
  // A. Audio Text-to-Speech Reader
  const ttsBtn = document.getElementById('tts-audio-btn');
  const ttsIcon = document.getElementById('tts-icon');
  const ttsText = document.getElementById('tts-text');

  if (ttsBtn && 'speechSynthesis' in window) {
    let utterance = null;
    let isSpeaking = false;

    ttsBtn.addEventListener('click', () => {
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        ttsBtn.classList.remove('playing');
        ttsIcon.className = 'fas fa-volume-up';
        ttsText.textContent = document.documentElement.lang === 'ta' ? 'செய்தியைக் கேளுங்கள்' : 'Listen to Story';
      } else {
        const title = document.querySelector('.article-main-title')?.textContent || '';
        const summary = document.querySelector('.article-content-body .lead')?.textContent || '';
        const textToRead = `${title}. ${summary}`;

        utterance = new SpeechSynthesisUtterance(textToRead);
        utterance.rate = 0.95;
        utterance.lang = document.documentElement.lang === 'ta' ? 'ta-IN' : 'en-US';

        utterance.onend = () => {
          isSpeaking = false;
          ttsBtn.classList.remove('playing');
          ttsIcon.className = 'fas fa-volume-up';
          ttsText.textContent = document.documentElement.lang === 'ta' ? 'மீண்டும் கேளுங்கள்' : 'Listen Again';
        };

        window.speechSynthesis.speak(utterance);
        isSpeaking = true;
        ttsBtn.classList.add('playing');
        ttsIcon.className = 'fas fa-pause';
        ttsText.textContent = document.documentElement.lang === 'ta' ? 'ஒலிக்கிறது... (நிறுத்து)' : 'Playing... (Pause)';
      }
    });
  }

  // B. Font Size Adjuster
  const articleBody = document.querySelector('.article-content-body');
  const fontBtns = document.querySelectorAll('.font-btn');

  if (articleBody && fontBtns.length > 0) {
    const fontSizes = {
      'font-decrease': '15px',
      'font-normal': '17px',
      'font-increase': '20px'
    };

    fontBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        fontBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const targetSize = fontSizes[btn.id] || '17px';
        articleBody.style.fontSize = targetSize;
      });
    });
  }

  // C. Interactive Like / Applaud Button with Floating Hearts
  const likeBtn = document.getElementById('like-article-btn');
  const likesCountEl = document.getElementById('likes-count');

  if (likeBtn) {
    likeBtn.addEventListener('click', async () => {
      const articleId = likeBtn.getAttribute('data-article-id');
      if (!articleId) return;

      // Spawn floating heart animation
      spawnFloatingHeart(likeBtn);

      try {
        const res = await fetch('/api/article/like', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ article_id: articleId })
        });
        const data = await res.json();
        if (data.success) {
          if (likesCountEl) likesCountEl.textContent = data.likes;
          likeBtn.classList.add('liked');
          showToast(document.documentElement.lang === 'ta' ? 'உங்கள் பாராட்டு பதிவு செய்யப்பட்டது! ❤️' : 'Thanks for applauding! ❤️', 'success');
        }
      } catch (err) {
        console.error('Like request failed:', err);
      }
    });
  }

  function spawnFloatingHeart(btn) {
    const heart = document.createElement('i');
    heart.className = 'fas fa-heart floating-heart';
    const rect = btn.getBoundingClientRect();
    heart.style.left = `${rect.left + rect.width / 2}px`;
    heart.style.top = `${rect.top}px`;
    const randomX = (Math.random() - 0.5) * 40;
    heart.style.setProperty('--tx', `${randomX}px`);
    document.body.appendChild(heart);
    setTimeout(() => heart.remove(), 950);
  }
}

/* ==========================================================================
   9. INTERACTIVE IMAGE LIGHTBOX MODAL
   ========================================================================== */
function initImageLightbox() {
  const modal = document.getElementById('image-lightbox-modal');
  const modalImg = document.getElementById('lightbox-img');
  const captionEl = document.getElementById('lightbox-caption');
  const closeBtn = document.getElementById('lightbox-close-btn');

  if (!modal || !modalImg) return;

  const triggers = document.querySelectorAll('.lightbox-trigger img');

  triggers.forEach(img => {
    img.addEventListener('click', () => {
      modalImg.src = img.src;
      if (captionEl) {
        captionEl.textContent = img.getAttribute('data-caption') || img.alt || '';
      }
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });
}

/* ==========================================================================
   9B. INTERACTIVE VIDEO LIGHTBOX MODAL
   ========================================================================== */
function initVideoLightbox() {
  const modal = document.getElementById('video-lightbox-modal');
  const iframe = document.getElementById('video-lightbox-iframe');
  const titleEl = document.getElementById('video-lightbox-title');
  const linkEl = document.getElementById('video-lightbox-link');
  const closeBtn = document.getElementById('video-lightbox-close-btn');

  if (!modal || !iframe) return;

  function closeModal() {
    modal.classList.remove('active');
    iframe.src = '';
    document.body.style.overflow = '';
  }

  document.querySelectorAll('.open-video-modal-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const videoId = btn.dataset.videoId;
      if (!videoId) return;

      e.preventDefault();
      iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&rel=0`;
      if (titleEl) titleEl.textContent = btn.dataset.videoTitle || 'Featured Video Report';
      if (linkEl) {
        linkEl.href = btn.dataset.articleUrl || '#';
      }
      modal.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });
}

/* ==========================================================================
   10. LIVE SEARCH AUTOCOMPLETE DROPDOWN
   ========================================================================== */
function initLiveSearch() {
  const searchInput = document.getElementById('header-search-input');
  const dropdown = document.getElementById('search-dropdown');
  if (!searchInput || !dropdown) return;

  let debounceTimer = null;

  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    const query = searchInput.value.trim();

    if (query.length < 2) {
      dropdown.classList.remove('active');
      dropdown.innerHTML = '';
      return;
    }

    debounceTimer = setTimeout(async () => {
      try {
        const res = await fetch(`/api/search/live?q=${encodeURIComponent(query)}`);
        const data = await res.json();

        if (data.results && data.results.length > 0) {
          dropdown.innerHTML = data.results.map(r => `
            <a href="/article/${r.slug}" class="search-item">
              <img src="${r.image || '/static/images/placeholder.jpg'}" alt="" onerror="this.src='/static/images/placeholder.jpg'">
              <div class="search-item-info">
                <div class="search-item-title">${highlightMatch(r.title, query)}</div>
                <div class="search-item-meta">
                  <span>${r.category}</span> &bull; <span>${r.date}</span>
                </div>
              </div>
            </a>
          `).join('');
          dropdown.classList.add('active');
        } else {
          dropdown.innerHTML = `
            <div style="padding: 16px; text-align: center; color: var(--text-muted); font-size: 13px;">
              ${document.documentElement.lang === 'ta' ? 'முடிவுகள் எதுவும் இல்லை' : 'No articles match your query'}
            </div>
          `;
          dropdown.classList.add('active');
        }
      } catch (err) {
        console.error('Search error:', err);
      }
    }, 250);
  });

  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.remove('active');
    }
  });

  function highlightMatch(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<mark style="background:#fef08a;color:#854d0e;padding:0 2px;border-radius:2px;">$1</mark>');
  }
}

/* ==========================================================================
   11. BOOKMARK TOGGLE WITH BOUNCE & BADGE UPDATE
   ========================================================================== */
function initBookmarks() {
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('.bookmark-action-btn');
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();

    const articleId = btn.getAttribute('data-article-id');
    if (!articleId) return;

    btn.style.transform = 'scale(1.25)';
    setTimeout(() => { btn.style.transform = ''; }, 200);

    try {
      const res = await fetch('/api/bookmark/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ article_id: articleId })
      });
      const data = await res.json();

      if (data.success) {
        btn.classList.toggle('active', data.is_bookmarked);
        const icon = btn.querySelector('i');
        if (icon) {
          icon.className = data.is_bookmarked ? 'fas fa-bookmark' : 'far fa-bookmark';
        }

        const badge = document.getElementById('bookmark-counter-badge');
        if (badge) badge.textContent = data.total_count;

        showToast(
          data.is_bookmarked 
            ? (document.documentElement.lang === 'ta' ? 'கட்டுரை சேமிக்கப்பட்டது! 🔖' : 'Article added to bookmarks! 🔖')
            : (document.documentElement.lang === 'ta' ? 'கட்டுரை நீக்கப்பட்டது' : 'Removed from bookmarks'),
          data.is_bookmarked ? 'success' : 'info'
        );
      }
    } catch (err) {
      console.error('Bookmark error:', err);
    }
  });
}

/* ==========================================================================
   12. COPY LINK BUTTON WITH TOOLTIP
   ========================================================================== */
function initCopyLinkButtons() {
  const copyBtn = document.getElementById('copy-article-link-btn');
  if (!copyBtn) return;

  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(window.location.href).then(() => {
      const originalHTML = copyBtn.innerHTML;
      copyBtn.innerHTML = '<i class="fas fa-check" style="color: #22c55e;"></i> Copied!';
      showToast(document.documentElement.lang === 'ta' ? 'இணைப்பு நகலெடுக்கப்பட்டது! 📋' : 'Link copied to clipboard! 📋', 'success');
      setTimeout(() => {
        copyBtn.innerHTML = originalHTML;
      }, 2000);
    }).catch(err => {
      console.error('Copy link failed:', err);
    });
  });
}

/* ==========================================================================
   13. AJAX NEWSLETTER SUBSCRIPTION
   ========================================================================== */
function initAjaxNewsletter() {
  const forms = document.querySelectorAll('.ajax-newsletter-form');
  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const emailInput = form.querySelector('input[name="email"]');
      if (!emailInput) return;

      const formData = new FormData(form);

      try {
        const res = await fetch('/subscribe', {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
          body: formData
        });
        const data = await res.json();

        if (data.status === 'success') {
          showToast(data.message, 'success');
          emailInput.value = '';
        } else {
          showToast(data.message || 'Error subscribing', 'danger');
        }
      } catch (err) {
        console.error('Newsletter error:', err);
        form.submit();
      }
    });
  });
}

/* ==========================================================================
   TOAST NOTIFICATIONS (Floating Animated Banner)
   ========================================================================== */
function showToast(message, type = 'info') {
  const container = document.querySelector('.toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast alert-${type}`;
  toast.innerHTML = `
    <span>${message}</span>
    <button type="button" style="background:transparent;border:none;color:inherit;cursor:pointer;font-size:16px;margin-left:auto;">&times;</button>
  `;

  toast.querySelector('button').addEventListener('click', () => toast.remove());
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOutRight 0.3s ease forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
