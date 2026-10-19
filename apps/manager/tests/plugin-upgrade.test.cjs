'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {gzipSync}=require('node:zlib');
const {fixture}=require('./fixture.cjs');
const {Manager}=require('../src/engine.cjs');
const {fs,path,readJSON,writeJSON,hashBytes,exists}=require('../src/paths.cjs');
const relative='kh2/dll/KH2FM_AR_PlaceTextShadow.dll';

for(const platform of ['win32','linux']) for(const version of ['1.0.19','1.0.20']) {
 test(platform+': '+version+' to2.0.0 installs and removes only the approved plugin',async()=>{
  const f=await fixture(platform);
  try {
   await f.manager.install(f.game);
   const old=await readJSON(path.join(f.dataDir,'manifest.json'));
   const stateFile=path.join(f.game,'.kh2fm-arabic/state.json'),before=await readJSON(stateFile);
   before.version=version;await writeJSON(stateFile,before);
   f.catalog.versions.find(x=>x.version===version).files=old.files.filter(x=>x.group==='payload');
   const bytes=await fs.readFile(path.join(__dirname,'../../..','native/place-text-shadow/KH2FM_AR_PlaceTextShadow.dll'));
   assert.equal(hashBytes(bytes),'b18ab9db0192b816e6f95efd3bc4ca983b8006a119a6b2794ad368d24a2e2986');
   const blob=await fs.readFile(path.join(f.dataDir,'payload.bin')),compressed=gzipSync(bytes),next=Buffer.concat([blob,compressed]);
   const manifest={...old,blobHash:hashBytes(next),files:[...old.files,{path:relative,group:'payload',size:bytes.length,sha256:hashBytes(bytes),offset:blob.length,compressedSize:compressed.length}]};
   f.catalog.versions.push({version:'2.0.0',files:manifest.files.filter(x=>x.group==='payload')});
   await fs.writeFile(path.join(f.dataDir,'payload.bin'),next);await writeJSON(path.join(f.dataDir,'manifest.json'),manifest);
   const manager=new Manager(f.options),target=path.join(before.modRoot,relative),other=path.join(before.modRoot,'kh2/dll/other-mod.dll');
   await fs.mkdir(path.dirname(other),{recursive:true});await fs.writeFile(other,'KEEP OTHER MOD');
   await manager.install(f.game);assert.deepEqual(await fs.readFile(target),bytes);
   await manager.undo(f.game);assert.equal(await exists(target),false);assert.equal((await manager.inspect(f.game)).version,version);
   // Adopt the exact approved local experiment so removal does not restore it.
   await fs.writeFile(target,bytes);await manager.install(f.game);
   assert.equal((await readJSON(stateFile)).entries.find(x=>x.path===relative).original,null);
   await manager.remove(f.game);assert.equal(await exists(target),false);
   assert.equal(await fs.readFile(other,'utf8'),'KEEP OTHER MOD');
   assert.equal(await fs.readFile(path.join(f.game,'save.dat'),'utf8'),'KEEP MY SAVE');
   await manager.undo(f.game);assert.deepEqual(await fs.readFile(target),bytes);
   await fs.writeFile(target,'USER EDIT');await assert.rejects(manager.remove(f.game));
   assert.equal(await fs.readFile(target,'utf8'),'USER EDIT');
   await writeJSON(path.join(f.dataDir,'manifest.json'),{...manifest,files:manifest.files.map(x=>x.path===relative?{...x,sha256:'f'.repeat(64)}:x)});
   await assert.rejects(manager.manifest(),/غير مسموح/);
  }finally{await f.cleanup();}
 });
}
