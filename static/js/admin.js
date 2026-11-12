/**
 * VITHAIGAL IYAKKAM - ADMIN DASHBOARD INTERACTIONS
 * Pure Vanilla JavaScript: Charts, Image Preview, Delete Modals, AJAX Toggles, Sidebar Drawer & Theme Toggle
 * Zero external JS dependencies.
 */

document.addEventListener('DOMContentLoaded', () => {
  initSidebarDrawer();
  initThemeToggle();
  initImageUploadPreview();
  initSlugAutoGenerator();
  initDeleteModals();
  initStatusToggles();
  initDashboardCharts();
  initTableQuickFilter();
  initCategoryInteractions();
  initBreakingNewsInteractions();
  initMessageInteractions();
  initVideoUrlPreview();
  initDynamicArticleBlocks();
});

/* ==========================================================================
   1. MOBILE & TABLET SIDEBAR DRAWER (Smooth Slide-In & Backdrop)
   ========================================================================== */
function initSidebarDrawer() {
  const sidebar = document.getElementById('admin-sidebar');
  const toggleBtn = document.getElementById('sidebar-toggle-btn');
  const closeBtn = document.getElementById('sidebar-close-btn');
  const overlay = document.getElementById('sidebar-backdrop-overlay');

  if (!sidebar) return;

  function openSidebar() {
    sidebar.classList.add('active');
    if (overlay) overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openSidebar();
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeSidebar();
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // Close sidebar on link click in mobile view
  const sidebarLinks = sidebar.querySelectorAll('.sidebar-menu a');
  sidebarLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 1024) {
        closeSidebar();
      }
    });
  });

  // Touch swipe to dismiss sidebar on mobile
  let touchStartX = 0;
  sidebar.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
  }, { passive: true });

  sidebar.addEventListener('touchend', (e) => {
    const touchEndX = e.changedTouches[0].clientX;
    if (touchStartX - touchEndX > 50) {
      closeSidebar();
    }
  }, { passive: true });

  // Close with Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeSidebar();
      const deleteModal = document.getElementById('delete-confirm-modal');
      if (deleteModal) deleteModal.classList.remove('active');
      const editCategoryModal = document.getElementById('edit-category-modal');
      if (editCategoryModal) editCategoryModal.classList.remove('active');
      const editTickerModal = document.getElementById('edit-ticker-modal');
      if (editTickerModal) editTickerModal.classList.remove('active');
      const viewMessageModal = document.getElementById('view-message-modal');
      if (viewMessageModal) viewMessageModal.classList.remove('active');
    }
  });
}

/* ==========================================================================
   2. DARK / LIGHT THEME TOGGLE (User-Side Shared Preference)
   ========================================================================== */
function initThemeToggle() {
  const themeBtns = document.querySelectorAll('.theme-toggle-btn');
  
  // Read preference from localStorage (shared with public site 'vi_theme')
  const savedTheme = localStorage.getItem('vi_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcons(savedTheme);

  themeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('vi_theme', newTheme);
      updateThemeIcons(newTheme);

      // Re-draw canvas charts to update background & axis colors
      if (window.redrawAdminCharts) {
        window.redrawAdminCharts();
      }

      showAdminToast(`Switched to ${newTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
    });
  });

  function updateThemeIcons(theme) {
    themeBtns.forEach(btn => {
      const icon = btn.querySelector('i');
      if (icon) {
        if (theme === 'dark') {
          icon.className = 'fas fa-sun';
          btn.setAttribute('title', 'Switch to Light Mode');
        } else {
          icon.className = 'fas fa-moon';
          btn.setAttribute('title', 'Switch to Dark Mode');
        }
      }
    });
  }
}

/* ==========================================================================
   3. TOAST NOTIFICATIONS (Interactive Visual Feedback)
   ========================================================================== */
function showAdminToast(message, type = 'info') {
  let container = document.getElementById('admin-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'admin-toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let iconHtml = '<i class="fas fa-info-circle"></i>';
  if (type === 'success') iconHtml = '<i class="fas fa-check-circle" style="color: #10b981;"></i>';
  if (type === 'danger') iconHtml = '<i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>';

  toast.innerHTML = `${iconHtml}<span>${message}</span>`;
  container.appendChild(toast);

  // Auto remove after 3.5s
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/* ==========================================================================
   4. IMAGE UPLOAD PREVIEW & VALIDATION
   ========================================================================== */
function initImageUploadPreview() {
  const fileInput = document.getElementById('featured_image');
  const previewImg = document.getElementById('image-preview');
  const dropzone = document.getElementById('image-dropzone');
  const sizeWarning = document.getElementById('file-size-warning');

  if (!fileInput) return;

  function handleFile(file) {
    if (!file) return;

    // Validate type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif', 'image/svg+xml'];
    if (!validTypes.includes(file.type)) {
      alert('Invalid file format. Please upload a JPG, PNG, WEBP, or GIF image.');
      fileInput.value = '';
      return;
    }

    // Validate size (max 5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      if (sizeWarning) sizeWarning.style.display = 'block';
      alert('Image file is too large! Maximum allowed size is 5MB.');
      fileInput.value = '';
      return;
    } else {
      if (sizeWarning) sizeWarning.style.display = 'none';
    }

    // Read and display preview
    const reader = new FileReader();
    reader.onload = (e) => {
      if (previewImg) {
        previewImg.src = e.target.result;
        previewImg.classList.add('visible');
      }
    };
    reader.readAsDataURL(file);
    showAdminToast('Image selected for upload', 'info');
  }

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  });

  // Drag and Drop support
  if (dropzone) {
    ['dragenter', 'dragover'].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.style.borderColor = 'var(--accent-orange)';
        dropzone.style.backgroundColor = 'rgba(255, 87, 34, 0.08)';
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropzone.addEventListener(name, (e) => {
        e.preventDefault();
        dropzone.style.borderColor = '';
        dropzone.style.backgroundColor = '';
      });
    });

    dropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        fileInput.files = e.dataTransfer.files;
        handleFile(e.dataTransfer.files[0]);
      }
    });

    dropzone.addEventListener('click', () => {
      fileInput.click();
    });
  }
}

/* ==========================================================================
   5. AUTOMATIC SEO SLUG GENERATOR
   ========================================================================== */
function initSlugAutoGenerator() {
  const titleInput = document.getElementById('title');
  const slugInput = document.getElementById('slug');

  if (!titleInput || !slugInput) return;

  titleInput.addEventListener('blur', () => {
    if (!slugInput.value.trim()) {
      const generated = titleInput.value
        .toLowerCase()
        .trim()
        .replace(/[^\w\s-]/g, '')
        .replace(/[\s_-]+/g, '-')
        .replace(/^-+|-+$/g, '');
      slugInput.value = generated;
    }
  });
}

/* ==========================================================================
   6. DELETE CONFIRMATION MODALS
   ========================================================================== */
function initDeleteModals() {
  const modalBackdrop = document.getElementById('delete-confirm-modal');
  const deleteForm = document.getElementById('delete-form');
  const modalItemName = document.getElementById('modal-item-name');
  const cancelBtn = document.getElementById('modal-cancel-btn');

  document.querySelectorAll('.open-delete-modal-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const actionUrl = btn.dataset.actionUrl;
      const itemName = btn.dataset.itemName || 'this record';

      if (deleteForm) deleteForm.action = actionUrl;
      if (modalItemName) modalItemName.textContent = itemName;
      if (modalBackdrop) modalBackdrop.classList.add('active');
    });
  });

  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      if (modalBackdrop) modalBackdrop.classList.remove('active');
    });
  }

  if (modalBackdrop) {
    modalBackdrop.addEventListener('click', (e) => {
      if (e.target === modalBackdrop) {
        modalBackdrop.classList.remove('active');
      }
    });
  }
}

/* ==========================================================================
   7. AJAX STATUS TOGGLES (Articles & Breaking News)
   ========================================================================== */
function initStatusToggles() {
  // 1. Article Status Toggle (Published <-> Draft)
  document.querySelectorAll('.toggle-article-status-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const articleId = btn.dataset.id;
      btn.style.opacity = '0.5';

      fetch(`/admin/articles/${articleId}/toggle-status`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(res => res.json())
      .then(data => {
        btn.style.opacity = '1';
        if (data.success) {
          btn.textContent = data.new_status;
          btn.className = `status-badge ${data.new_status} toggle-article-status-btn`;
          showAdminToast(`Article status updated to ${data.new_status.toUpperCase()}`, 'success');
        }
      })
      .catch(() => {
        btn.style.opacity = '1';
        showAdminToast('Failed to update article status', 'danger');
      });
    });
  });

  // 2. Breaking News Toggle (Active <-> Inactive)
  document.querySelectorAll('.toggle-breaking-news-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const newsId = btn.dataset.id;
      btn.style.opacity = '0.5';

      fetch(`/admin/breaking-news/toggle/${newsId}`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(res => res.json())
      .then(data => {
        btn.style.opacity = '1';
        if (data.success) {
          const statusText = data.is_active ? 'Active' : 'Inactive';
          btn.textContent = statusText;
          btn.className = `status-badge ${data.is_active ? 'active' : 'inactive'} toggle-breaking-news-btn`;
          showAdminToast(`Ticker item marked ${statusText}`, 'success');
        }
      })
      .catch(() => {
        btn.style.opacity = '1';
        showAdminToast('Failed to toggle breaking news status', 'danger');
      });
    });
  });
}

/* ==========================================================================
   8. CLIENT-SIDE INSTANT TABLE QUICK FILTER
   ========================================================================== */
function initTableQuickFilter() {
  const searchInputs = document.querySelectorAll('.table-search-input');
  searchInputs.forEach(input => {
    // Only bind client-side live filter if input has no form or if user types
    const table = input.closest('.card-table-wrap')?.querySelector('.admin-table');
    if (!table) return;

    input.addEventListener('input', () => {
      const filter = input.value.toLowerCase().trim();
      const rows = table.querySelectorAll('tbody tr');

      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
      });
    });
  });
}

/* ==========================================================================
   9. HIGH-DPI RETINA HTML5 CANVAS CHARTS (Zero external dependencies)
   ========================================================================== */
function initDashboardCharts() {
  function renderAllCharts() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

    // 1. Category Bar Chart
    const categoryCanvas = document.getElementById('categoryBarChart');
    if (categoryCanvas && window.categoryChartLabels && window.categoryChartData) {
      drawCategoryBarChart(categoryCanvas, window.categoryChartLabels, window.categoryChartData, isDark);
    }

    // 2. Status Donut Chart
    const statusCanvas = document.getElementById('statusDonutChart');
    if (statusCanvas && window.statusChartLabels && window.statusChartData) {
      drawStatusDonutChart(statusCanvas, window.statusChartLabels, window.statusChartData, isDark);
    }
  }

  // Initial draw
  renderAllCharts();

  // Expose global redraw function for theme switch
  window.redrawAdminCharts = renderAllCharts;

  // Responsive resize with debounce
  let resizeTimeout;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(renderAllCharts, 150);
  });
}

function drawCategoryBarChart(canvas, labels, data, isDark = false) {
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 2;
  
  canvas.width = rect.width * dpr;
  canvas.height = 260 * dpr;
  ctx.scale(dpr, dpr);

  const width = rect.width;
  const height = 260;
  const paddingBottom = 42;
  const paddingTop = 24;
  const paddingLeft = 40;
  const paddingRight = 20;
  const chartHeight = height - paddingTop - paddingBottom;
  const chartWidth = width - paddingLeft - paddingRight;

  const maxVal = Math.max(...data, 5);

  ctx.clearRect(0, 0, width, height);

  // Background Grid Lines & Axis Numbers
  ctx.strokeStyle = isDark ? '#1e293b' : '#e2e8f0';
  ctx.lineWidth = 1;
  const gridSteps = 4;
  ctx.fillStyle = isDark ? '#94a3b8' : '#64748b';
  ctx.font = '11px Inter, sans-serif';
  ctx.textAlign = 'right';

  for (let i = 0; i <= gridSteps; i++) {
    const y = paddingTop + (chartHeight / gridSteps) * i;
    const val = Math.round(maxVal - (maxVal / gridSteps) * i);
    ctx.beginPath();
    ctx.moveTo(paddingLeft, y);
    ctx.lineTo(width - paddingRight, y);
    ctx.stroke();
    ctx.fillText(val, paddingLeft - 8, y + 4);
  }

  // Draw Bars
  if (!labels.length) return;
  const barWidth = Math.min(38, (chartWidth / labels.length) - 12);
  const gap = (chartWidth - (barWidth * labels.length)) / (labels.length + 1);

  labels.forEach((label, i) => {
    const val = data[i] || 0;
    const barHeight = (val / maxVal) * chartHeight;
    const x = paddingLeft + gap + i * (barWidth + gap);
    const y = paddingTop + chartHeight - barHeight;

    // Gradient bar fill (Navy into Coral Orange)
    const grad = ctx.createLinearGradient(0, y, 0, y + barHeight);
    grad.addColorStop(0, '#ff5722');
    grad.addColorStop(1, '#e64a19');
    ctx.fillStyle = grad;

    // Rounded top bar
    drawRoundedRect(ctx, x, y, barWidth, barHeight, 4);

    // Value on top of bar
    ctx.fillStyle = isDark ? '#f8fafc' : '#0f172a';
    ctx.font = 'bold 11px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(val, x + barWidth / 2, y - 6);

    // Category Label below bar
    ctx.fillStyle = isDark ? '#cbd5e1' : '#475569';
    ctx.font = '11px Inter, sans-serif';
    const displayLabel = label.length > 8 ? label.substring(0, 7) + '..' : label;
    ctx.fillText(displayLabel, x + barWidth / 2, height - 16);
  });
}

function drawStatusDonutChart(canvas, labels, data, isDark = false) {
  const ctx = canvas.getContext('2d');
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 2;
  
  canvas.width = rect.width * dpr;
  canvas.height = 260 * dpr;
  ctx.scale(dpr, dpr);

  const width = rect.width;
  const height = 260;
  const centerX = width / 2;
  const centerY = height / 2 - 12;
  const radius = 68;
  const innerRadius = 44;

  const total = data.reduce((a, b) => a + b, 0) || 0;
  // Matching user side status colors: Green (Published), Amber (Draft), Sky Blue (Scheduled)
  const colors = ['#10b981', '#f59e0b', '#0ea5e9'];

  let startAngle = -Math.PI / 2;

  ctx.clearRect(0, 0, width, height);

  if (total > 0) {
    data.forEach((val, i) => {
      const sliceAngle = (val / total) * 2 * Math.PI;
      const endAngle = startAngle + sliceAngle;

      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, startAngle, endAngle);
      ctx.arc(centerX, centerY, innerRadius, endAngle, startAngle, true);
      ctx.closePath();
      ctx.fillStyle = colors[i % colors.length];
      ctx.fill();

      startAngle = endAngle;
    });
  } else {
    // Empty state ring
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.arc(centerX, centerY, innerRadius, 2 * Math.PI, 0, true);
    ctx.closePath();
    ctx.fillStyle = isDark ? '#1e293b' : '#e2e8f0';
    ctx.fill();
  }

  // Center Text (Total count)
  ctx.fillStyle = isDark ? '#f8fafc' : '#0f172a';
  ctx.font = 'bold 22px Inter, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(total, centerX, centerY - 2);

  ctx.fillStyle = isDark ? '#94a3b8' : '#64748b';
  ctx.font = '10px Inter, sans-serif';
  ctx.fillText('Articles', centerX, centerY + 16);

  // Legend at bottom
  const legendY = height - 16;
  ctx.font = '11.5px Inter, sans-serif';
  ctx.textBaseline = 'alphabetic';

  if (labels.length > 0) {
    const itemWidth = width / labels.length;

    labels.forEach((label, i) => {
      const x = itemWidth * i + itemWidth / 2;
      ctx.fillStyle = colors[i % colors.length];
      ctx.beginPath();
      ctx.arc(x - 26, legendY - 4, 5, 0, 2 * Math.PI);
      ctx.fill();

      ctx.fillStyle = isDark ? '#cbd5e1' : '#475569';
      ctx.textAlign = 'left';
      ctx.fillText(`${label} (${data[i] || 0})`, x - 16, legendY);
    });
  }
}

function drawRoundedRect(ctx, x, y, width, height, radius) {
  if (height <= 0) return;
  radius = Math.min(radius, height / 2, width / 2);
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height);
  ctx.lineTo(x, y + height);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
  ctx.fill();
}

/* ==========================================================================
   10. CATEGORY INTERACTIONS (Icon Preview & Edit Modal)
   ========================================================================== */
function initCategoryInteractions() {
  // Live Icon Preview
  function bindIconPreview(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    if (!input || !preview) return;

    input.addEventListener('input', () => {
      let iconName = input.value.trim().replace(/^fa[srb]?\s+fa-/, '').replace(/^fa-/, '');
      if (!iconName) iconName = 'folder';
      preview.innerHTML = `<i class="fas fa-${iconName}"></i>`;
    });
  }
  bindIconPreview('category-icon-input', 'category-icon-preview');
  bindIconPreview('edit-category-icon-input', 'edit-category-icon-preview');

  // Edit Category Modal
  const editModal = document.getElementById('edit-category-modal');
  const editForm = document.getElementById('edit-category-form');
  const editCloseBtns = document.querySelectorAll('.close-edit-category-modal-btn');

  document.querySelectorAll('.open-edit-category-modal-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const id = btn.dataset.id;
      const nameEn = btn.dataset.nameEn || '';
      const nameTa = btn.dataset.nameTa || '';
      const slug = btn.dataset.slug || '';
      const icon = btn.dataset.icon || 'newspaper';
      const order = btn.dataset.order || '1';
      const descEn = btn.dataset.descEn || '';
      const descTa = btn.dataset.descTa || '';

      if (editForm) editForm.action = `/admin/categories/edit/${id}`;
      
      const elNameEn = document.getElementById('edit-name-en');
      const elNameTa = document.getElementById('edit-name-ta');
      const elSlug = document.getElementById('edit-slug');
      const elIcon = document.getElementById('edit-category-icon-input');
      const elOrder = document.getElementById('edit-order');
      const elDescEn = document.getElementById('edit-desc-en');
      const elDescTa = document.getElementById('edit-desc-ta');
      const elPreview = document.getElementById('edit-category-icon-preview');

      if (elNameEn) elNameEn.value = nameEn;
      if (elNameTa) elNameTa.value = nameTa;
      if (elSlug) elSlug.value = slug;
      if (elIcon) elIcon.value = icon;
      if (elOrder) elOrder.value = order;
      if (elDescEn) elDescEn.value = descEn;
      if (elDescTa) elDescTa.value = descTa;
      if (elPreview) elPreview.innerHTML = `<i class="fas fa-${icon}"></i>`;

      if (editModal) editModal.classList.add('active');
    });
  });

  editCloseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (editModal) editModal.classList.remove('active');
    });
  });

  if (editModal) {
    editModal.addEventListener('click', (e) => {
      if (e.target === editModal) editModal.classList.remove('active');
    });
  }
}

/* ==========================================================================
   11. BREAKING NEWS INTERACTIONS (Edit Modal)
   ========================================================================== */
function initBreakingNewsInteractions() {
  const editModal = document.getElementById('edit-ticker-modal');
  const editForm = document.getElementById('edit-ticker-form');
  const editCloseBtns = document.querySelectorAll('.close-edit-ticker-modal-btn');

  document.querySelectorAll('.open-edit-ticker-modal-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const id = btn.dataset.id;
      const title = btn.dataset.title || '';
      const titleTa = btn.dataset.titleTa || '';
      const link = btn.dataset.link || '';
      const order = btn.dataset.order || '1';
      const isActive = btn.dataset.active === 'true';

      if (editForm) editForm.action = `/admin/breaking-news/edit/${id}`;

      const elTitle = document.getElementById('edit-ticker-title');
      const elTitleTa = document.getElementById('edit-ticker-title-ta');
      const elLink = document.getElementById('edit-ticker-link');
      const elOrder = document.getElementById('edit-ticker-order');
      const elActive = document.getElementById('edit-ticker-active');

      if (elTitle) elTitle.value = title;
      if (elTitleTa) elTitleTa.value = titleTa;
      if (elLink) elLink.value = link;
      if (elOrder) elOrder.value = order;
      if (elActive) elActive.checked = isActive;

      if (editModal) editModal.classList.add('active');
    });
  });

  editCloseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (editModal) editModal.classList.remove('active');
    });
  });

  if (editModal) {
    editModal.addEventListener('click', (e) => {
      if (e.target === editModal) editModal.classList.remove('active');
    });
  }
}

/* ==========================================================================
   12. READER MESSAGES INTERACTIONS (AJAX Mark-Read & View Modal)
   ========================================================================== */
function initMessageInteractions() {
  // 1. AJAX Toggle Read / Unread Status Badge
  document.querySelectorAll('.toggle-message-read-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const messageId = btn.dataset.id;
      btn.style.opacity = '0.5';

      fetch(`/admin/messages/${messageId}/mark-read`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(res => res.json())
      .then(data => {
        btn.style.opacity = '1';
        if (data.success) {
          if (data.is_read) {
            btn.innerHTML = '<i class="fas fa-check-double"></i> Read';
            btn.className = 'status-badge published toggle-message-read-btn';
            btn.title = 'Click to mark as unread';
            showAdminToast('Message marked as Read', 'success');
          } else {
            btn.innerHTML = '<i class="fas fa-envelope"></i> New / Unread';
            btn.className = 'status-badge draft toggle-message-read-btn';
            btn.title = 'Click to mark as read';
            showAdminToast('Message marked as Unread', 'info');
          }
        }
      })
      .catch(() => {
        btn.style.opacity = '1';
        showAdminToast('Failed to update message status', 'danger');
      });
    });
  });

  // 2. View Message Modal Details
  const viewModal = document.getElementById('view-message-modal');
  const viewCloseBtns = document.querySelectorAll('.close-view-message-modal-btn');
  const modalSender = document.getElementById('view-modal-sender');
  const modalEmail = document.getElementById('view-modal-email');
  const modalDate = document.getElementById('view-modal-date');
  const modalSubject = document.getElementById('view-modal-subject');
  const modalBody = document.getElementById('view-modal-body');
  const modalReplyBtn = document.getElementById('view-modal-reply-btn');
  const modalMarkToggleBtn = document.getElementById('view-modal-mark-toggle-btn');

  document.querySelectorAll('.open-view-message-modal-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const id = btn.dataset.id;
      const name = btn.dataset.name || 'Unknown Reader';
      const email = btn.dataset.email || '';
      const date = btn.dataset.date || '';
      const subject = btn.dataset.subject || 'No Subject';
      const message = btn.dataset.message || '';
      const isRead = btn.dataset.read === 'true';

      if (modalSender) modalSender.textContent = name;
      if (modalEmail) {
        modalEmail.textContent = email;
        modalEmail.href = `mailto:${email}?subject=Re: ${encodeURIComponent(subject)}`;
      }
      if (modalDate) modalDate.textContent = date;
      if (modalSubject) modalSubject.textContent = subject;
      if (modalBody) modalBody.textContent = message;

      if (modalReplyBtn) {
        modalReplyBtn.href = `mailto:${email}?subject=Re: ${encodeURIComponent(subject)}`;
      }

      if (modalMarkToggleBtn) {
        modalMarkToggleBtn.dataset.id = id;
        modalMarkToggleBtn.innerHTML = isRead ? '<i class="fas fa-envelope"></i> Mark as Unread' : '<i class="fas fa-check-double"></i> Mark as Read';
        modalMarkToggleBtn.className = isRead ? 'admin-btn admin-btn-outline' : 'admin-btn admin-btn-secondary';
      }

      if (viewModal) viewModal.classList.add('active');
    });
  });

  if (modalMarkToggleBtn) {
    modalMarkToggleBtn.addEventListener('click', () => {
      const msgId = modalMarkToggleBtn.dataset.id;
      if (!msgId) return;

      modalMarkToggleBtn.style.opacity = '0.5';
      fetch(`/admin/messages/${msgId}/mark-read`, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(res => res.json())
      .then(data => {
        modalMarkToggleBtn.style.opacity = '1';
        if (data.success) {
          modalMarkToggleBtn.innerHTML = data.is_read ? '<i class="fas fa-envelope"></i> Mark as Unread' : '<i class="fas fa-check-double"></i> Mark as Read';
          modalMarkToggleBtn.className = data.is_read ? 'admin-btn admin-btn-outline' : 'admin-btn admin-btn-secondary';

          // Update corresponding row badge in table if present
          const rowBadge = document.querySelector(`.toggle-message-read-btn[data-id="${msgId}"]`);
          if (rowBadge) {
            if (data.is_read) {
              rowBadge.innerHTML = '<i class="fas fa-check-double"></i> Read';
              rowBadge.className = 'status-badge published toggle-message-read-btn';
            } else {
              rowBadge.innerHTML = '<i class="fas fa-envelope"></i> New / Unread';
              rowBadge.className = 'status-badge draft toggle-message-read-btn';
            }
          }
          showAdminToast(`Message marked as ${data.is_read ? 'Read' : 'Unread'}`, 'success');
        }
      })
      .catch(() => {
        modalMarkToggleBtn.style.opacity = '1';
        showAdminToast('Failed to toggle status', 'danger');
      });
    });
  }

  viewCloseBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (viewModal) viewModal.classList.remove('active');
    });
  });

  if (viewModal) {
    viewModal.addEventListener('click', (e) => {
      if (e.target === viewModal) viewModal.classList.remove('active');
    });
  }
}

/* ==========================================================================
   13. VIDEO URL LIVE EMBED & THUMBNAIL AUTO-DETECTION
   ========================================================================== */
function initVideoUrlPreview() {
  const videoInput = document.getElementById('video_url');
  const previewWrapper = document.getElementById('video-preview-wrapper');
  const iframe = document.getElementById('admin-video-iframe');
  const label = document.getElementById('video-detected-label');
  const useThumbBtn = document.getElementById('use-video-thumb-btn');
  const imageUrlInput = document.getElementById('image_url');
  const imagePreview = document.getElementById('image-preview');

  if (!videoInput || !previewWrapper || !iframe) return;

  function extractYouTubeId(url) {
    if (!url) return null;
    const clean = url.trim();
    if (/^[\w-]{11}$/.test(clean)) return clean;
    const regExp = /(?:https?:\/\/)?(?:www\.|m\.|music\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=|shorts\/))([\w-]{11})/;
    const match = clean.match(regExp);
    return match ? match[1] : null;
  }

  function updateVideoPreview() {
    const val = videoInput.value.trim();
    const ytId = extractYouTubeId(val);

    if (ytId) {
      const embedUrl = `https://www.youtube.com/embed/${ytId}?rel=0`;
      if (iframe.src !== embedUrl) {
        iframe.src = embedUrl;
      }
      if (label) {
        label.textContent = `YouTube Video Connected (ID: ${ytId})`;
      }
      previewWrapper.style.display = 'block';

      if (useThumbBtn) {
        useThumbBtn.onclick = (e) => {
          e.preventDefault();
          const thumbUrl = `https://img.youtube.com/vi/${ytId}/hqdefault.jpg`;
          if (imageUrlInput) imageUrlInput.value = thumbUrl;
          if (imagePreview) {
            imagePreview.src = thumbUrl;
            imagePreview.style.display = 'block';
            imagePreview.classList.add('visible');
          }
          showAdminToast('Video thumbnail set as featured image!', 'success');
        };
      }
    } else {
      iframe.src = '';
      previewWrapper.style.display = 'none';
    }
  }

  videoInput.addEventListener('input', updateVideoPreview);
  videoInput.addEventListener('change', updateVideoPreview);
  videoInput.addEventListener('paste', () => {
    setTimeout(updateVideoPreview, 50);
  });

  // Run on initial load if video URL exists
  if (videoInput.value && videoInput.value.trim()) {
    updateVideoPreview();
  }
}

/* ==========================================================================
   12. DYNAMIC SUMMARY & CONTENT BLOCKS ("Add Summary" & "Add Content")
   ========================================================================== */
function initDynamicArticleBlocks() {
  const addSummaryBtn = document.getElementById('add-summary-btn');
  const addContentBtn = document.getElementById('add-content-btn');
  const summariesContainer = document.getElementById('summaries-container');
  const contentsContainer = document.getElementById('contents-container');

  if (addSummaryBtn && summariesContainer) {
    addSummaryBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const existingItems = summariesContainer.querySelectorAll('.dynamic-block-item');
      const nextIndex = existingItems.length + 1;

      const block = document.createElement('div');
      block.className = 'dynamic-block-item';
      block.dataset.index = nextIndex;
      block.innerHTML = `
        <div class="dynamic-block-header">
          <span class="dynamic-block-title">
            <i class="fas fa-align-left" style="color: var(--accent-orange);"></i>
            Short Summary / Excerpt #${nextIndex}
          </span>
          <button type="button" class="remove-block-btn" title="Remove this summary block">
            <i class="fas fa-trash-alt"></i> Remove
          </button>
        </div>
        <div class="form-group-admin">
          <label>Short Summary / Excerpt (English)</label>
          <textarea name="summary" class="admin-textarea" style="min-height: 80px;" placeholder="Brief 1-2 sentence overview for cards and meta descriptions..."></textarea>
        </div>
        <div class="form-group-admin">
          <label>Short Summary / Excerpt (Tamil / தமிழ்)</label>
          <textarea name="summary_ta" class="admin-textarea" style="min-height: 80px;" placeholder="சுருக்கமான அறிமுக உரை..."></textarea>
        </div>
      `;

      summariesContainer.appendChild(block);
      
      const newTextarea = block.querySelector('textarea');
      if (newTextarea) newTextarea.focus();

      // Hook up remove button
      const removeBtn = block.querySelector('.remove-block-btn');
      if (removeBtn) {
        removeBtn.addEventListener('click', () => {
          block.remove();
          reindexBlocks(summariesContainer, 'Short Summary / Excerpt');
        });
      }
    });
  }

  if (addContentBtn && contentsContainer) {
    addContentBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const existingItems = contentsContainer.querySelectorAll('.dynamic-block-item');
      const nextIndex = existingItems.length + 1;

      const block = document.createElement('div');
      block.className = 'dynamic-block-item';
      block.dataset.index = nextIndex;
      block.innerHTML = `
        <div class="dynamic-block-header">
          <span class="dynamic-block-title">
            <i class="fas fa-paragraph" style="color: var(--accent-orange);"></i>
            Full Article Content #${nextIndex}
          </span>
          <button type="button" class="remove-block-btn" title="Remove this content block">
            <i class="fas fa-trash-alt"></i> Remove
          </button>
        </div>
        <div class="form-group-admin">
          <label>Full Article Content (HTML / Text)</label>
          <textarea name="content" class="admin-textarea" style="min-height: 180px;" placeholder="Full editorial article body (supports <p>, <h3>, <blockquote>, <ul>, etc.)..."></textarea>
        </div>
        <div class="form-group-admin">
          <label>Full Article Content (Tamil / தமிழ்)</label>
          <textarea name="content_ta" class="admin-textarea" style="min-height: 180px;" placeholder="முழுமையான தமிழ்க் கட்டுரை உரை..."></textarea>
        </div>
      `;

      contentsContainer.appendChild(block);

      const newTextarea = block.querySelector('textarea');
      if (newTextarea) newTextarea.focus();

      // Hook up remove button
      const removeBtn = block.querySelector('.remove-block-btn');
      if (removeBtn) {
        removeBtn.addEventListener('click', () => {
          block.remove();
          reindexBlocks(contentsContainer, 'Full Article Content');
        });
      }
    });
  }

  // Hook up any pre-existing remove buttons
  document.querySelectorAll('.remove-block-btn').forEach(btn => {
    btn.addEventListener('click', function() {
      const block = this.closest('.dynamic-block-item');
      if (block) {
        const parent = block.parentElement;
        block.remove();
        if (parent && parent.id === 'summaries-container') {
          reindexBlocks(parent, 'Short Summary / Excerpt');
        } else if (parent && parent.id === 'contents-container') {
          reindexBlocks(parent, 'Full Article Content');
        }
      }
    });
  });

  function reindexBlocks(container, labelPrefix) {
    const items = container.querySelectorAll('.dynamic-block-item');
    items.forEach((item, idx) => {
      item.dataset.index = idx + 1;
      const titleSpan = item.querySelector('.dynamic-block-title');
      if (titleSpan) {
        const icon = titleSpan.querySelector('i');
        const iconHtml = icon ? icon.outerHTML : '';
        titleSpan.innerHTML = `${iconHtml} ${labelPrefix} #${idx + 1}`;
      }
    });
  }
}




