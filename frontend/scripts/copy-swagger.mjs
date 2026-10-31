import { copyFile } from 'node:fs/promises';
for (const name of ['swagger-ui.css', 'swagger-ui-bundle.js']) {
  await copyFile(`node_modules/swagger-ui-dist/${name}`, `dist/${name}`);
}
