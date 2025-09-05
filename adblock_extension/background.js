// Background script for ad blocking
var blockedDomains = [
  "*://*.googlesyndication.com/*",
  "*://*.doubleclick.net/*",
  "*://*.googleadservices.com/*",
  "*://*.adsystem.amazon.com/*",
  "*://*.facebook.com/tr/*",
  "*://*.pubmatic.com/*",
  "*://*.outbrain.com/*",
  "*://*.taboola.com/*",
  "*://*.criteo.com/*",
  "*://*.betweendigital.com/*",
  "*://*.adroll.com/*",
  "*://*.hotjar.com/*",
  "*://*.segment.com/*",
  "*://*.pinterest.com/*",
  "*://*.linkedin.com/*",
  "*://*.twitter.com/*",
  "*://*.youtube.com/*",
  "*://*.vimeo.com/*"
];

chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    // Block requests to known ad domains
    for (var i = 0; i < blockedDomains.length; i++) {
      if (details.url.match(blockedDomains[i].replace(/\*/g, '.*'))) {
        console.log('Blocked ad request:', details.url);
        return {cancel: true};
      }
    }
    return {cancel: false};
  },
  {urls: ["<all_urls>"]},
  ["blocking"]
);

// Also block by referrer
chrome.webRequest.onBeforeSendHeaders.addListener(
  function(details) {
    var headers = details.requestHeaders;
    for (var i = 0; i < headers.length; i++) {
      if (headers[i].name.toLowerCase() === 'referer') {
        // If referrer contains ad-related domains, block
        if (headers[i].value.includes('googlesyndication') ||
            headers[i].value.includes('doubleclick') ||
            headers[i].value.includes('facebook.com/tr')) {
          console.log('Blocked by referrer:', headers[i].value);
          return {cancel: true};
        }
      }
    }
    return {requestHeaders: headers};
  },
  {urls: ["<all_urls>"]},
  ["blocking", "requestHeaders"]
);
