#!/usr/bin/env node

/**
 * Performance testing script
 * Run with: node scripts/test-performance.js
 */

const { execSync } = require('child_process');
const fs = require('fs');

console.log('🧪 Running performance tests...');

// Check if the development server is running
function checkServer() {
  try {
    const response = execSync('curl -s -o /dev/null -w "%{http_code}" http://localhost:3000', { encoding: 'utf8' });
    return response.trim() === '200';
  } catch (error) {
    return false;
  }
}

// Test API response time
function testAPI() {
  try {
    const start = Date.now();
    execSync('curl -s http://localhost:8000/v1/machines?limit=5', { encoding: 'utf8' });
    const end = Date.now();
    return end - start;
  } catch (error) {
    return null;
  }
}

// Check bundle size
function checkBundleSize() {
  try {
    if (fs.existsSync('.next/static/chunks')) {
      const files = fs.readdirSync('.next/static/chunks');
      let totalSize = 0;
      files.forEach(file => {
        if (file.endsWith('.js')) {
          const stats = fs.statSync(`.next/static/chunks/${file}`);
          totalSize += stats.size;
        }
      });
      return totalSize / 1024; // KB
    }
  } catch (error) {
    return null;
  }
  return null;
}

// Run tests
console.log('\n📊 Performance Test Results:');

if (!checkServer()) {
  console.log('❌ Development server not running. Start with: npm run dev');
  process.exit(1);
}

console.log('✅ Development server is running');

const apiTime = testAPI();
if (apiTime) {
  console.log(`✅ API response time: ${apiTime}ms`);
  if (apiTime < 200) {
    console.log('   🎉 Excellent performance!');
  } else if (apiTime < 500) {
    console.log('   ⚠️  Good performance, could be improved');
  } else {
    console.log('   🚨 Slow performance, needs optimization');
  }
} else {
  console.log('❌ API test failed');
}

const bundleSize = checkBundleSize();
if (bundleSize) {
  console.log(`✅ Bundle size: ${bundleSize.toFixed(1)}KB`);
  if (bundleSize < 500) {
    console.log('   🎉 Excellent bundle size!');
  } else if (bundleSize < 1000) {
    console.log('   ⚠️  Good bundle size, could be optimized');
  } else {
    console.log('   🚨 Large bundle size, needs optimization');
  }
} else {
  console.log('❌ Bundle size check failed (run build first)');
}

console.log('\n📋 Next Steps:');
console.log('1. Run: npm run build');
console.log('2. Run: npm run analyze');
console.log('3. Run: npm run lighthouse');
console.log('4. Check the PERFORMANCE_OPTIMIZATION.md guide');

console.log('\n✅ Performance test complete!');
