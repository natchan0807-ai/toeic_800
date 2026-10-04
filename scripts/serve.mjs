import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve(import.meta.dirname,'../dist');
const port=Number(process.env.PORT || 5173);
const host=process.env.HOST || '127.0.0.1';
const mime={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.webmanifest':'application/manifest+json','.svg':'image/svg+xml','.png':'image/png'};
const server=http.createServer((req,res)=>{
  let pathname;
  try { pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname); } catch {res.writeHead(400).end();return;}
  const file=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
  if (!file.startsWith(root+path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {res.writeHead(404).end('Not found');return;}
  res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'});
  fs.createReadStream(file).pipe(res);
});
server.on('error',error=>{console.error(`起動できません: ${error.code}。ポート${port}の利用権限・使用状況を確認してください。`);process.exitCode=1;});
server.listen(port,host,()=>console.log(`STEP 800 → http://localhost:${port} （終了: Ctrl+C / 待受 ${host}）`));
