import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';

const output = resolve('../.local/finnova-preview.html');
let html = await readFile('dist/index.html', 'utf8');
const script = html.match(/<script\b[^>]*src="([^"]+)"[^>]*><\/script>/);
const style = html.match(/<link\b[^>]*href="([^"]+\.css)"[^>]*>/);
if (!script || !style) throw new Error('Expected one Vite entry script and stylesheet. Run the build first.');

const javascript = await readFile(resolve('dist', script[1].replace(/^\//, '')), 'utf8');
const css = await readFile(resolve('dist', style[1].replace(/^\//, '')), 'utf8');
const icon = await readFile('public/favicon.svg', 'utf8');
html = html.replace('<html ', '<html data-preview="visual" ')
  .replace(script[0], () => `<script type="module">${javascript.replace(/<\/script/gi, '<\\/script')}</script>`)
  .replace(style[0], () => `<style>${css}</style>`)
  .replace('href="/favicon.svg"', `href="data:image/svg+xml,${encodeURIComponent(icon)}"`);
await mkdir(dirname(output), { recursive: true });
await writeFile(output, html);
const interactive = html.replace('data-preview="visual"', 'data-preview="interactive"');
await writeFile(resolve('../.local/finnova-demo.html'), interactive);
console.log('Standalone outputs: .local/finnova-preview.html (visual) and .local/finnova-demo.html (fictional interactive demo).');
