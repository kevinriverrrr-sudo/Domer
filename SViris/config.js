// API Configuration for VirusTotal
const CONFIG = {
  VIRUSTOTAL_API_KEY: 'b3c6edf1e32e42feebebd9d485205b3f748e36cf1be71e1c6c9c5bda181c6af6',
  VIRUSTOTAL_API_URL: 'https://www.virustotal.com/api/v3',
  MAX_FILE_SIZE: 32 * 1024 * 1024, // 32MB
  SCAN_TIMEOUT: 60000 // 60 seconds
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
}
