/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
    '../django_shop/shop/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};

