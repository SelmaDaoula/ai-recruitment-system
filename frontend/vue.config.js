module.exports = {
  outputDir: 'build',  // IMPORTANT : Create React App utilise 'build'
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}