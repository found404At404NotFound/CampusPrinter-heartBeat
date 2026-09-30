const https = require('https');

const TARGET_URL = process.env.TARGET_URL;

function ping(url) {
  return new Promise((resolve) => {
    const start = Date.now();
    const req = https.get(url, { timeout: 25000 }, (res) => {
      let body = '';
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => {
        resolve({
          status: res.statusCode,
          ms: Date.now() - start,
          bytes: body.length,
        });
      });
    });
    req.on('error', (err) => resolve({ error: err.message, ms: Date.now() - start }));
    req.on('timeout', () => { req.destroy(); resolve({ error: 'timeout', ms: Date.now() - start }); });
  });
}

module.exports = async function (req, res) {
  if (!TARGET_URL) {
    console.error('TARGET_URL env var is not set');
    return res.json({ ok: false, error: 'TARGET_URL not configured' }, 500);
  }

  const result = await ping(TARGET_URL);
  console.log('Keep-alive ping:', TARGET_URL, JSON.stringify(result));
  return res.json({ ok: result.status === 200, target: TARGET_URL, ...result });
};
