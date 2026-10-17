'use strict';
const os=require('node:os');
const zlib=require('node:zlib');
const {fs,path,hashBytes,writeJSON}=require('../src/paths.cjs');
const {GAME_EXE}=require('../src/compatibility.cjs');
const {Manager}=require('../src/engine.cjs');

async function fixture(platform='win32') {
  const tempBase=await fs.realpath(os.tmpdir());
  const root=await fs.mkdtemp(path.join(tempBase,'kh2fm-103-'));
  const game=platform==='darwin' ? path.join(root,'Bottle','drive_c','Game') : path.join(root,'Steam','steamapps','common','KINGDOM HEARTS -HD 1.5+2.5 ReMIX-');
  const prefix=platform==='darwin' ? path.join(root,'Bottle') : path.join(root,'Steam','steamapps','compatdata','2552430','pfx');
  const dataDir=path.join(root,'data'); await fs.mkdir(game,{recursive:true}); await fs.mkdir(dataDir,{recursive:true});
  await fs.writeFile(path.join(game,GAME_EXE),'ORIGINAL GAME EXECUTABLE');
  await fs.writeFile(path.join(game,'save.dat'),'KEEP MY SAVE');
  if (platform!=='win32') { await fs.mkdir(prefix,{recursive:true}); await fs.writeFile(path.join(prefix,'user.reg'),'WINE REGISTRY Version 2\n\n[Software\\\\Wine\\\\DllOverrides]\n"other"="native"\n'); }
  const {FONT_FOLDER}=require('../src/font-runtime.cjs');
  const payload=['kh2/msg/us/fontimage.bar','kh2/msg/us/fontinfo.bar',...Array.from({length:3},(_,i)=>FONT_FOLDER+'/US_fontimage_bar'+i+'.png'),'kh2/msg/us/sys.bar','kh2/msg/us/tt.bar','kh2/msg/us/eh.bar','kh2/fontimage.png'];
  const loaderData=Buffer.from('Test Panacea loader: panacea_settings.txt');
  const catalog={versions:['1.0.1','1.0.2','1.0.4','1.0.5','1.0.6','1.0.7','1.0.8','1.0.9'].map(version=>({version,files:payload.map(p=>({path:p,sha256:hashBytes(Buffer.from(version+':'+p)),size:Buffer.byteLength(version+':'+p)}))})),loader:[{path:'DBGHELP.dll',sha256:hashBytes(loaderData),size:loaderData.length}]};
  catalog.loader.push({...catalog.loader[0],path:'version.dll'});
  const files=[]; const chunks=[]; let offset=0;
  for (const p of [...payload,'DBGHELP.dll','version.dll']) {
    const group=p.startsWith('kh2/') ? 'payload' : 'loader';
    const bytes=group==='payload' ? Buffer.from('1.0.10:'+p) : loaderData;
    const compressed=zlib.gzipSync(bytes);
    files.push({path:p,group,size:bytes.length,sha256:hashBytes(bytes),offset,compressedSize:compressed.length});
    chunks.push(compressed); offset+=compressed.length;
  }
  const blob=Buffer.concat(chunks);
  await fs.writeFile(path.join(dataDir,'payload.bin'),blob);
  await writeJSON(path.join(dataDir,'manifest.json'),{schema:1,version:'1.0.10',blobHash:hashBytes(blob),files});
  const options={dataDir,catalog,platform};
  const manager=new Manager(options);
  return {root,game,prefix,dataDir,catalog,options,manager,payload,loaderData,cleanup:()=>fs.rm(root,{recursive:true,force:true})};
}
async function legacy(f,version='1.0.1') {
  const app=path.join(f.root,'KH2FM-Arabic'),mod=path.join(app,'mod');
  for (const file of f.catalog.versions.find(x=>x.version===version).files) {
    const target=path.join(mod,...file.path.split('/')); await fs.mkdir(path.dirname(target),{recursive:true}); await fs.writeFile(target,version+':'+file.path);
  }
  await fs.writeFile(path.join(f.game,'DBGHELP.dll'),f.loaderData);
  const simulateWineOnWindows=process.platform==='win32' && f.options.platform!=='win32';
  const configuredMod=simulateWineOnWindows ? path.relative(f.game,mod).split(path.sep).join('/') : mod;
  const configuredGame=simulateWineOnWindows ? '.' : f.game;
  await fs.writeFile(path.join(f.game,'panacea_settings.txt'),'mod_path='+configuredMod+'\nshow_console=false\n');
  await fs.writeFile(path.join(app,'kh2ar_state.txt'),'GameDir='+configuredGame+'\nModRoot='+configuredMod+'\nSettingsByUs=1\n');
  await fs.writeFile(path.join(app,'kh2ar_backups.txt'),'');
  return {app,mod};
}
module.exports={fixture,legacy};
