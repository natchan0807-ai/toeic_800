import ts from '../tools/typescript/typescript.js';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
const root = path.resolve(import.meta.dirname, '..');
process.chdir(root);
const config = ts.readConfigFile('tsconfig.json', ts.sys.readFile);
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, root);
const checkOnly = process.argv.includes('--check');
const program = ts.createProgram(parsed.fileNames, {...parsed.options, noEmit: checkOnly});
const diagnostics = ts.getPreEmitDiagnostics(program);
if (diagnostics.length) {
  console.error(ts.formatDiagnosticsWithColorAndContext(diagnostics, {
    getCanonicalFileName: f => f, getCurrentDirectory: () => root, getNewLine: () => '\n'
  }));
  process.exit(1);
}
if (checkOnly) { console.log(`TypeScript ${ts.version}: 型チェック成功`); process.exit(0); }
fs.rmSync('dist', {recursive:true,force:true});
program.emit();
fs.cpSync('public','dist',{recursive:true});
if (fs.existsSync('content/master.json')) {
  fs.mkdirSync('dist/data',{recursive:true});
  fs.copyFileSync('content/master.json','dist/data/content.json');
}
const files = fs.readdirSync('dist',{recursive:true}).filter(f=>fs.statSync(path.join('dist',f)).isFile() && f !== 'sw.js');
const hash = crypto.createHash('sha256');
files.forEach(f=>hash.update(fs.readFileSync(path.join('dist',f))));
const version = hash.digest('hex').slice(0,12);
const sw = fs.readFileSync('scripts/sw-template.js','utf8')
  .replace('__CACHE_VERSION__',version).replace('__PRECACHE_FILES__',JSON.stringify(files.map(f=>'./'+f.split(path.sep).join('/'))));
fs.writeFileSync('dist/sw.js',sw);
console.log(`ビルド成功: ${files.length} files / ${version} → dist/`);
