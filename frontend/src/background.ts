/**
 * Chrome Extension Background Service Worker
 * Handles extension lifecycle, OAuth, and background tasks
 */

chrome.runtime.onInstalled.addListener((details) => {
  console.log('AI Email Grouping Extension installed', details);
  
  if (details.reason === 'install') {
    // First-time installation
    chrome.storage.local.set({ 
      installed: true,
      installedDate: new Date().toISOString()
    });
  }
});

// Handle OAuth flow
chrome.identity.onSignInChanged.addListener((account, signedIn) => {
  console.log('Sign in status changed', account, signedIn);
  if (signedIn) {
    // User signed in - ready to process emails
    chrome.runtime.sendMessage({ type: 'AUTH_SUCCESS', account });
  }
});

// Message handler for content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message);
  
  switch (message.type) {
    case 'GET_AUTH_TOKEN':
      // Get OAuth token for Gmail API
      chrome.identity.getAuthToken(
        { interactive: true },
        (token) => {
          if (chrome.runtime.lastError) {
            sendResponse({ error: chrome.runtime.lastError.message });
          } else {
            sendResponse({ token });
          }
        }
      );
      return true; // Keep channel open for async response
    
    case 'PROCESS_EMAILS':
      // Trigger email processing
      // This will be implemented in later tasks
      sendResponse({ status: 'queued' });
      break;
    
    default:
      sendResponse({ error: 'Unknown message type' });
  }
  
  return true;
});

