/**
 * Content Script for Gmail
 * Injects sidebar and interacts with Gmail interface
 * TASK-025: Enhanced Gmail integration with state management
 */

// Sidebar container reference
let sidebarContainer: HTMLElement | null = null;
let sidebarFrame: HTMLIFrameElement | null = null;

/**
 * Inject sidebar into Gmail
 * Creates iframe to isolate React app from Gmail's DOM
 */
function injectSidebar() {
  // Check if sidebar already exists
  if (document.getElementById('tradie-email-grouping-sidebar')) {
    return;
  }

  // Create sidebar container
  sidebarContainer = document.createElement('div');
  sidebarContainer.id = 'tradie-email-grouping-sidebar';
  sidebarContainer.className = 'tradie-sidebar-container';
  
  // Create iframe for React app (isolates from Gmail's DOM)
  sidebarFrame = document.createElement('iframe');
  sidebarFrame.id = 'tradie-sidebar-iframe';
  sidebarFrame.src = chrome.runtime.getURL('sidebar.html');
  sidebarFrame.style.cssText = `
    width: 100%;
    height: 100%;
    border: none;
    background: transparent;
  `;
  
  sidebarContainer.appendChild(sidebarFrame);
  
  // Inject sidebar CSS
  const style = document.createElement('link');
  style.rel = 'stylesheet';
  style.href = chrome.runtime.getURL('content.css');
  document.head.appendChild(style);

  // Append sidebar to document body
  document.body.appendChild(sidebarContainer);

  // Adjust Gmail layout to accommodate sidebar
  adjustGmailLayout();
  
  // Listen for messages from sidebar
  window.addEventListener('message', handleSidebarMessage);
}

/**
 * Adjust Gmail layout to make room for sidebar
 */
function adjustGmailLayout() {
  // Find Gmail's main content area
  const mainContent = document.querySelector('[role="main"]') as HTMLElement;
  if (mainContent) {
    // Add margin to prevent overlap
    mainContent.style.marginRight = '320px';
    mainContent.style.transition = 'margin-right 0.3s ease-in-out';
  }

  // Adjust Gmail's app container if it exists
  const appContainer = document.querySelector('[role="application"]') as HTMLElement;
  if (appContainer) {
    appContainer.style.paddingRight = '0';
  }
}

/**
 * Handle messages from sidebar iframe
 */
function handleSidebarMessage(event: MessageEvent) {
  // Only accept messages from our extension
  if (event.source !== sidebarFrame?.contentWindow) {
    return;
  }

  const { type, data } = event.data;

  switch (type) {
    case 'SIDEBAR_COLLAPSED':
      // Collapse sidebar
      if (sidebarContainer) {
        sidebarContainer.classList.add('collapsed');
        const mainContent = document.querySelector('[role="main"]') as HTMLElement;
        if (mainContent) {
          mainContent.style.marginRight = '0';
        }
      }
      break;
    
    case 'SIDEBAR_EXPANDED':
      // Expand sidebar
      if (sidebarContainer) {
        sidebarContainer.classList.remove('collapsed');
        adjustGmailLayout();
      }
      break;
    
    case 'SELECT_PROJECT':
      // Handle project selection
      if (data?.projectId) {
        // Store selected project
        chrome.storage.local.set({ selectedProjectId: data.projectId });
        // Could trigger Gmail label filtering here
      }
      break;
    
    default:
      console.log('Unknown message type:', type);
  }
}

/**
 * Send message to sidebar
 */
function sendToSidebar(type: string, data?: any) {
  if (sidebarFrame?.contentWindow) {
    sidebarFrame.contentWindow.postMessage({ type, data }, '*');
  }
}

/**
 * Watch for Gmail navigation changes (SPA)
 */
let lastUrl = location.href;
const urlObserver = new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    // Maintain sidebar across navigation
    if (!document.getElementById('tradie-email-grouping-sidebar')) {
      injectSidebar();
    }
    // Notify sidebar of navigation
    sendToSidebar('GMAIL_NAVIGATION', { url });
  }
});

// Watch for Gmail DOM changes to maintain sidebar
const domObserver = new MutationObserver(() => {
  // Ensure sidebar is still present
  if (!document.getElementById('tradie-email-grouping-sidebar')) {
    injectSidebar();
  }
  
  // Re-adjust layout if Gmail structure changed
  adjustGmailLayout();
});

// Initialize sidebar
function initSidebar() {
  // Wait for Gmail to fully load
  const checkGmailReady = setInterval(() => {
    const gmailContainer = document.querySelector('[role="main"]');
    if (gmailContainer) {
      clearInterval(checkGmailReady);
      injectSidebar();
      
      // Start observing for changes
      urlObserver.observe(document, { subtree: true, childList: true });
      domObserver.observe(document.body, { subtree: true, childList: true });
    }
  }, 100);
  
  // Timeout after 10 seconds
  setTimeout(() => {
    clearInterval(checkGmailReady);
  }, 10000);
}

// Start initialization
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSidebar);
} else {
  initSidebar();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  urlObserver.disconnect();
  domObserver.disconnect();
  window.removeEventListener('message', handleSidebarMessage);
});

