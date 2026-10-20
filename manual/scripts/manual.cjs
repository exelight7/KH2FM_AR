'use strict';
const fs=require('node:fs/promises');
const path=require('node:path');
const os=require('node:os');
const crypto=require('node:crypto');
const {execFileSync,spawnSync}=require('node:child_process');
const {createInterface}=require('node:readline/promises');
const root=path.resolve(__dirname,'..');
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const exeName='KINGDOM HEARTS II FINAL MIX.exe';
async function integrity(){
  const lines=(await fs.readFile(path.join(root,'SHA256SUMS.txt'),'utf8')).trim().split('\n');
  for(const line of lines){
    const match=/^([a-f0-9]{64})  (.+)$/.exec(line.trim());
    if(!match || match[2].includes('\\') || match[2].includes(':') || match[2].split('/').some(x=>!x || x==='..' || x==='.') || path.isAbsolute(match[2]))throw Error('Invalid checksum path');
    if(digest(await fs.readFile(path.join(root,match[2])))!==match[1])throw Error('Damaged package: '+match[2]);
  }
}
async function exists(file){try{return (await fs.stat(file)).isFile();}catch{return false;}}
async function steamGames(){
  const bases=new Set([path.join(process.env['ProgramFiles(x86)']||'C:/Program Files (x86)','Steam')]);
  try{
    const reg=execFileSync('reg.exe',['query','HKCU\\Software\\Valve\\Steam','/v','SteamPath'],{encoding:'utf8',windowsHide:true});
    const match=/SteamPath\s+REG_SZ\s+(.+)/i.exec(reg);if(match)bases.add(match[1].trim());
  }catch{/* A custom folder can be selected without Steam registry access. */}
  for(const base of [...bases]){
    try{for(const match of (await fs.readFile(path.join(base,'steamapps/libraryfolders.vdf'),'utf8')).matchAll(/"path"\s+"([^"]+)"/g))bases.add(match[1].replaceAll('\\\\','\\'));}catch{}
  }
  const games=[];
  for(const base of bases){const game=path.join(base,'steamapps/common/KINGDOM HEARTS -HD 1.5+2.5 ReMIX-');if(await exists(path.join(game,exeName)))games.push(game);}
  return [...new Set(games)];
}
async function chooseGame(given){
  if(given)return path.resolve(given.replace(/^"|"$/g,''));
  const games=await steamGames();if(games.length===1)return games[0];
  if(!process.stdin.isTTY)throw Error('Specify --game followed by the game directory');
  const input=createInterface({input:process.stdin,output:process.stdout});
  try{return path.resolve((await input.question('Paste the Steam game directory: ')).trim().replace(/^"|"$/g,''));}finally{input.close();}
}
function closed(){
  const rows=execFileSync('tasklist.exe',['/FI','IMAGENAME eq '+exeName,'/FO','CSV','/NH'],{encoding:'utf8',windowsHide:true});
  if(rows.toLowerCase().includes(exeName.toLowerCase()))throw Error('Save your progress and close KH2 before continuing.');
}
async function compatible(game,manifest){
  if(digest(await fs.readFile(path.join(game,exeName)))!==manifest.exeHash)throw Error('Unsupported or unknown game version. Installation aborted to prevent damage.');
  for(const [name,hash] of Object.entries(manifest.heds)){
    if(digest(await fs.readFile(path.join(game,'Image/dt',name)))!==hash)throw Error('Unsupported or changed game archive index: '+name);
    if(!await exists(path.join(game,'Image/dt',name.replace(/\.hed$/,'.pkg'))))throw Error('Missing original game archive: '+name);
  }
}
async function main(args=process.argv.slice(2)){
  const operation=args.shift()||'install';
  if(!['install','remove','undo','verify','check'].includes(operation))throw Error('Unknown operation');
  let given=null;
  if(args.length){if(args.length!==2 || args[0]!=='--game')throw Error('Usage: install|remove|undo|verify|check [--game directory]');given=args[1];}
  await integrity();
  const game=await chooseGame(given);
  const original=JSON.parse(await fs.readFile(path.join(root,'files/manual-manifest.json'),'utf8'));
  if(['install','check'].includes(operation))await compatible(game,original);
  if(operation==='check'){console.log('PASS: package checksums and supported Steam game version. Game files were not changed.');return;}
  closed();
  const {Manager}=require('../engine/engine.cjs');
  const {hash}=require('../engine/paths.cjs');
  const catalog=require('../engine/legacy.json');
  let dataDir=path.join(root,'files');
  if(operation==='install'){
    const cache=path.join(process.env.LOCALAPPDATA||os.tmpdir(),'KH2FM-Arabic/manual-cache',digest(Buffer.from(game.toLowerCase())).slice(0,20),'2.0.1');
    let ready=false;
    try{const m=JSON.parse(await fs.readFile(path.join(cache,'manifest.json'),'utf8'));const official=JSON.parse(await fs.readFile(path.join(root,'files/manifest.json'),'utf8'));
      ready=m.version==='2.0.1' && m.files.length===official.files.length && official.files.every(e=>m.files.some(f=>f.path===e.path && f.group===e.group && f.sha256===e.sha256 && f.size===e.size)) && await hash(path.join(cache,'payload.bin'))===m.blobHash;}catch{}
    if(!ready){
      // Each attempt owns a fresh directory; an interrupted attempt cannot be reused.
      const pending=cache+'-'+crypto.randomUUID();await fs.mkdir(path.dirname(cache),{recursive:true});
      const child=spawnSync(path.join(root,'tools/ManualAssets.exe'),['prepare',path.join(root,'files/manual-manifest.json'),game,pending],{stdio:'inherit',windowsHide:true});
      if(child.error)throw child.error;if(child.status!==0)throw Error('Arabic file preparation failed. No mod files were installed. Temporary files: '+pending);
      if(await fs.stat(cache).catch(()=>false))await fs.rename(cache,cache+'-previous-'+crypto.randomUUID());
      await fs.rename(pending,cache);
    }
    dataDir=cache;
  }
  const manager=new Manager({dataDir,catalog,platform:'win32'});
  if(operation==='verify'){
    const c=await manager.context(game);if(!c.state)throw Error('No managed Arabic installation found');
    for(const entry of c.state.entries)if(await hash(path.join(entry.root==='mod'?c.modRoot:game,entry.path))!==entry.sha256)throw Error('Installed file changed: '+entry.path);
    console.log('PASS: installed version '+c.state.version+'; all managed file hashes verified.');return;
  }
  closed();
  let lastProgress='';
  const result=await manager[operation](game,{progress:p=>{const label=p.phase+' '+Math.floor(10*p.current/Math.max(1,p.total))*10+'%';if(label!==lastProgress){console.log(label);lastProgress=label;}}});
  console.log(JSON.stringify(result));
  console.log(operation==='install'?'Arabic 2.0.1 is ready. Start KH2 normally from Steam.':'Operation completed. Backups and unrelated files are preserved.');
}
module.exports={main,steamGames,integrity};
if(require.main===module)main().catch(error=>{console.error('ERROR: '+error.message);process.exitCode=1;});
