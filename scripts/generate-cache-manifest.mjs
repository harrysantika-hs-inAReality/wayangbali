import { createHash } from 'node:crypto';
import { readdir, readFile, stat, writeFile } from 'node:fs/promises';
import { join, relative, sep } from 'node:path';

const root = join(process.cwd(), 'dist');
const excluded = new Set(['asset-manifest.json', 'index.html', 'queue.php', 'tutor.php', '.htaccess', 'sw.js']);

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(path));
    else files.push(path);
  }
  return files;
}

const paths = (await walk(root)).sort();
const hash = createHash('sha256');
const files = [];
for (const path of paths) {
  const name = relative(root, path).split(sep).join('/');
  if (excluded.has(name)) continue;
  const metadata = await stat(path);
  const content = await readFile(path);
  hash.update(name).update(content);
  files.push({ url: `/${name}`, size: metadata.size });
}

const manifest = {
  version: hash.digest('hex').slice(0, 16),
  totalBytes: files.reduce((total, file) => total + file.size, 0),
  files,
};

await writeFile(join(root, 'asset-manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`);
