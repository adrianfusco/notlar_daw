/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./notlar/templates/*.html",
    "./notlar/static/js/*.js",
    //"./node_modules/flowbite/**/*.js"
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("flowbite/plugin")
  ]
}
