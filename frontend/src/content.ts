/**
 * Content Script for Gmail
 * Injects sidebar and interacts with Gmail interface
 */

// Inject sidebar into Gmail
function injectSidebar() {
  // Check if sidebar already exists
  if (document.getElementById('tradie-email-grouping-sidebar')) {
    return;
  }

  // Create sidebar container
  const sidebar = document.createElement('div');
  sidebar.id = 'tradie-email-grouping-sidebar';
  sidebar.innerHTML = `
    <div id="tradie-sidebar-content">
      <div class="tradie-sidebar-header">
        <h3>Project Groups</h3>
        <button id="tradie-sidebar-toggle">−</button>
      </div>
      <div class="tradie-sidebar-body">
        <div id="tradie-projects-list">Loading projects...</div>
      </div>
    </div>
  `;

  // Inject sidebar CSS
  const style = document.createElement('link');
  style.rel = 'stylesheet';
  style.href = chrome.runtime.getURL('sidebar.css');
  document.head.appendChild(style);

  // Append sidebar to Gmail's main container
  const gmailContainer = document.querySelector('[role="main"]') || document.body;
  gmailContainer.appendChild(sidebar);

  // Load sidebar script
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('sidebar.js');
  script.onload = () => script.remove();
  document.head.appendChild(script);
}

// Wait for Gmail to load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', injectSidebar);
} else {
  injectSidebar();
}

// Listen for navigation changes in Gmail (SPA)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    // Re-inject sidebar if needed
    if (!document.getElementById('tradie-email-grouping-sidebar')) {
      injectSidebar();
    }
  }
}).observe(document, { subtree: true, childList: true });

