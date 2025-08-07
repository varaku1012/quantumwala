import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const loginSuccessRate = new Rate('login_success');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 1000 },  // Ramp up to 1000 users
    { duration: '10m', target: 10000 }, // Ramp up to 10000 users
    { duration: '5m', target: 1000 },  // Scale down to 1000 users
    { duration: '2m', target: 0 },     // Scale down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% of requests under 500ms
    http_req_failed: ['rate<0.05'],                  // Error rate under 5%
    errors: ['rate<0.05'],                           // Custom error rate under 5%
    login_success: ['rate>0.95'],                    // 95% login success rate
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3001/api/v1';

// Test data
const testUsers = [];
for (let i = 0; i < 10000; i++) {
  testUsers.push({
    email: `testuser${i}@example.com`,
    password: 'TestP@ssw0rd123',
  });
}

// Helper functions
function randomUser() {
  return testUsers[Math.floor(Math.random() * testUsers.length)];
}

// Setup: Create test users
export function setup() {
  console.log('Creating test users...');
  const responses = [];
  
  for (let i = 0; i < 100; i++) {
    const res = http.post(`${BASE_URL}/auth/register`, JSON.stringify(testUsers[i]), {
      headers: { 'Content-Type': 'application/json' },
    });
    responses.push(res);
  }

  return { testUsers: testUsers.slice(0, 100) };
}

// Main test scenarios
export default function (data) {
  // Scenario weights
  const scenario = Math.random();
  
  if (scenario < 0.4) {
    // 40% - Login scenario
    testLogin();
  } else if (scenario < 0.6) {
    // 20% - Token refresh scenario
    testTokenRefresh();
  } else if (scenario < 0.8) {
    // 20% - Protected endpoint access
    testProtectedEndpoint();
  } else if (scenario < 0.9) {
    // 10% - Registration scenario
    testRegistration();
  } else {
    // 10% - Password reset scenario
    testPasswordReset();
  }

  sleep(Math.random() * 2); // Random think time between 0-2 seconds
}

function testLogin() {
  const user = randomUser();
  const payload = JSON.stringify({
    email: user.email,
    password: user.password,
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'login' },
  };

  const res = http.post(`${BASE_URL}/auth/login`, payload, params);

  const success = check(res, {
    'login status is 200': (r) => r.status === 200,
    'login response has token': (r) => r.json('tokens.accessToken') !== '',
    'login response time < 200ms': (r) => r.timings.duration < 200,
  });

  errorRate.add(!success);
  loginSuccessRate.add(success);

  return res.json();
}

function testTokenRefresh() {
  // First login to get tokens
  const loginData = testLogin();
  
  if (loginData && loginData.tokens) {
    sleep(1); // Wait before refresh

    const payload = JSON.stringify({
      refreshToken: loginData.tokens.refreshToken,
    });

    const params = {
      headers: { 'Content-Type': 'application/json' },
      tags: { name: 'refresh' },
    };

    const res = http.post(`${BASE_URL}/auth/refresh`, payload, params);

    check(res, {
      'refresh status is 200': (r) => r.status === 200,
      'refresh returns new token': (r) => r.json('tokens.accessToken') !== '',
      'refresh response time < 100ms': (r) => r.timings.duration < 100,
    });
  }
}

function testProtectedEndpoint() {
  // First login to get token
  const loginData = testLogin();

  if (loginData && loginData.tokens) {
    const params = {
      headers: {
        'Authorization': `Bearer ${loginData.tokens.accessToken}`,
      },
      tags: { name: 'protected' },
    };

    const res = http.get(`${BASE_URL}/auth/me`, params);

    check(res, {
      'protected endpoint status is 200': (r) => r.status === 200,
      'protected endpoint returns user': (r) => r.json('id') !== '',
      'protected endpoint response time < 50ms': (r) => r.timings.duration < 50,
    });
  }
}

function testRegistration() {
  const timestamp = Date.now();
  const payload = JSON.stringify({
    email: `newuser${timestamp}@example.com`,
    password: 'NewP@ssw0rd123',
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'register' },
  };

  const res = http.post(`${BASE_URL}/auth/register`, payload, params);

  check(res, {
    'registration status is 201': (r) => r.status === 201,
    'registration returns user': (r) => r.json('user.email') !== '',
    'registration response time < 300ms': (r) => r.timings.duration < 300,
  });
}

function testPasswordReset() {
  const user = randomUser();
  const payload = JSON.stringify({
    email: user.email,
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'password-reset' },
  };

  const res = http.post(`${BASE_URL}/auth/forgot-password`, payload, params);

  check(res, {
    'password reset status is 200': (r) => r.status === 200,
    'password reset response time < 100ms': (r) => r.timings.duration < 100,
  });
}

// Teardown: Clean up test data
export function teardown(data) {
  console.log('Test completed. Cleaning up...');
}

// Custom summary
export function handleSummary(data) {
  return {
    'performance-report.html': htmlReport(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

function htmlReport(data) {
  return `
<!DOCTYPE html>
<html>
<head>
    <title>Authentication Service Performance Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .metric { margin: 20px 0; padding: 20px; background: #f5f5f5; border-radius: 8px; }
        .success { color: green; }
        .failure { color: red; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #4CAF50; color: white; }
    </style>
</head>
<body>
    <h1>Authentication Service Performance Test Results</h1>
    
    <div class="metric">
        <h2>Test Configuration</h2>
        <p>Maximum Virtual Users: 10,000</p>
        <p>Test Duration: 24 minutes</p>
        <p>Base URL: ${BASE_URL}</p>
    </div>

    <div class="metric">
        <h2>Key Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Threshold</th>
                <th>Status</th>
            </tr>
            <tr>
                <td>95th Percentile Response Time</td>
                <td>${data.metrics.http_req_duration.values['p(95)']}ms</td>
                <td>&lt; 500ms</td>
                <td class="${data.metrics.http_req_duration.values['p(95)'] < 500 ? 'success' : 'failure'}">
                    ${data.metrics.http_req_duration.values['p(95)'] < 500 ? 'PASS' : 'FAIL'}
                </td>
            </tr>
            <tr>
                <td>Error Rate</td>
                <td>${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%</td>
                <td>&lt; 5%</td>
                <td class="${data.metrics.http_req_failed.values.rate < 0.05 ? 'success' : 'failure'}">
                    ${data.metrics.http_req_failed.values.rate < 0.05 ? 'PASS' : 'FAIL'}
                </td>
            </tr>
            <tr>
                <td>Login Success Rate</td>
                <td>${(data.metrics.login_success.values.rate * 100).toFixed(2)}%</td>
                <td>&gt; 95%</td>
                <td class="${data.metrics.login_success.values.rate > 0.95 ? 'success' : 'failure'}">
                    ${data.metrics.login_success.values.rate > 0.95 ? 'PASS' : 'FAIL'}
                </td>
            </tr>
        </table>
    </div>

    <div class="metric">
        <h2>Endpoint Performance</h2>
        <table>
            <tr>
                <th>Endpoint</th>
                <th>Requests</th>
                <th>Avg Response Time</th>
                <th>95th Percentile</th>
                <th>Error Rate</th>
            </tr>
            ${Object.entries(data.metrics)
                .filter(([key, value]) => key.startsWith('http_req_duration{name:'))
                .map(([key, value]) => {
                    const name = key.match(/name:([^}]+)/)[1];
                    return `
                    <tr>
                        <td>${name}</td>
                        <td>${value.values.count}</td>
                        <td>${value.values.avg.toFixed(2)}ms</td>
                        <td>${value.values['p(95)'].toFixed(2)}ms</td>
                        <td>N/A</td>
                    </tr>
                    `;
                }).join('')}
        </table>
    </div>

    <div class="metric">
        <h2>Test Summary</h2>
        <p>Total Requests: ${data.metrics.http_reqs.values.count}</p>
        <p>Total Data Received: ${(data.metrics.data_received.values.count / 1024 / 1024).toFixed(2)} MB</p>
        <p>Total Data Sent: ${(data.metrics.data_sent.values.count / 1024 / 1024).toFixed(2)} MB</p>
        <p>Average RPS: ${(data.metrics.http_reqs.values.rate).toFixed(2)}</p>
    </div>

    <div class="metric">
        <h2>Recommendations</h2>
        <ul>
            ${data.metrics.http_req_duration.values['p(95)'] > 500 ? 
                '<li>Response times exceed threshold. Consider optimizing database queries and adding caching.</li>' : ''}
            ${data.metrics.http_req_failed.values.rate > 0.05 ? 
                '<li>Error rate is high. Check application logs and scaling configuration.</li>' : ''}
            ${data.metrics.login_success.values.rate < 0.95 ? 
                '<li>Login success rate is below target. Verify authentication logic and database performance.</li>' : ''}
            ${data.metrics.http_reqs.values.rate < 1000 ? 
                '<li>Request rate is lower than expected. Check for bottlenecks in the system.</li>' : ''}
        </ul>
    </div>

    <div class="metric">
        <p>Generated at: ${new Date().toISOString()}</p>
    </div>
</body>
</html>
  `;
}