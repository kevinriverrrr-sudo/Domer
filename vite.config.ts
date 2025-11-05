import { defineConfig } from 'vite';
import { copyFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

export default defineConfig({
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        content: 'src/content.ts',
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  },
  plugins: [
    {
      name: 'copy-manifest',
      closeBundle() {
        // Copy manifest.json
        copyFileSync('manifest.json', 'dist/manifest.json');
        
        // Copy icons directory if it exists
        if (existsSync('icons')) {
          mkdirSync('dist/icons', { recursive: true });
          copyFileSync('icons/icon.svg', 'dist/icons/icon.svg');
        }
      }
    }
  ]
});