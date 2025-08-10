#!/usr/bin/env node

/**
 * Performance optimization script for the frontend
 * Run with: node scripts/optimize.js
 */

const fs = require('fs');
const path = require('path');

console.log('🔧 Running performance optimizations...');

// Check for common performance issues
const checks = [
  {
    name: 'Next.js config exists',
    check: () => fs.existsSync('next.config.js'),
    fix: () => console.log('✅ Next.js config found')
  },
  {
    name: 'Package.json has performance scripts',
    check: () => {
      const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      return pkg.scripts && (pkg.scripts.build || pkg.scripts.analyze);
    },
    fix: () => console.log('✅ Build scripts found')
  },
  {
    name: 'Tailwind config optimized',
    check: () => {
      const config = fs.readFileSync('tailwind.config.js', 'utf8');
      return config.includes('purge') || config.includes('content');
    },
    fix: () => console.log('✅ Tailwind purge configured')
  }
];

// Run checks
checks.forEach(({ name, check, fix }) => {
  if (check()) {
    fix();
  } else {
    console.log(`⚠️  ${name} - needs attention`);
  }
});

// Performance recommendations
console.log('\n📋 Performance Recommendations:');
console.log('1. Use Next.js Image component for optimized images');
console.log('2. Implement lazy loading for components');
console.log('3. Use React.memo for expensive components');
console.log('4. Implement proper caching strategies');
console.log('5. Consider using a CDN for static assets');
console.log('6. Optimize bundle size with code splitting');
console.log('7. Use compression (gzip/brotli)');
console.log('8. Implement service worker for caching');

console.log('\n✅ Performance optimization check complete!');
