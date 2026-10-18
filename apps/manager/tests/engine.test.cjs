'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {fs,path,hash,hashBytes,readJSON,writeJSON,exists}=require('../src/paths.cjs');
const {REG_LINE,REG_SECTION,registryValue,patchRegistry,GAME_EXE}=require('../src/compatibility.cjs');
const {fixture,legacy}=require('./fixture.cjs');
const {FONT_FOLDER}=require('../src/font-runtime.cjs');

test('reinstall skips matching payload bytes and repairs only a missing file',async()=>withFixture('win32',async f=>{
  await f.manager.install(f.game);
  const state=await readJSON(path.join(f.game,'.kh2fm-arabic/state.json'));
  let copies=[];await f.manager.install(f.game,{afterWrite:(_,action)=>{if(action.source && action.target.startsWith(state.modRoot+path.sep))copies.push(action.target);}});
  assert.deepEqual(copies,[]);
  const missing=path.join(state.modRoot,f.payload[0]);await fs.rm(missing);
  copies=[];await f.manager.install(f.game,{afterWrite:(_,action)=>{if(action.source && action.target.startsWith(state.modRoot+path.sep))copies.push(action.target);}});
  assert.deepEqual(copies,[missing]);assert.deepEqual((await f.manager.inspect(f.game)).fontCheck.issues,[]);
  await f.manager.undo(f.game);assert.equal(await exists(missing),false);
}));
for(const version of ['1.0.10','1.0.11','1.0.12']) test('upgrade from '+version+' retains saved font conflicts and restores them on removal',async()=>withFixture('win32',async f=>{
  const old=await legacy(f),target=path.join(old.mod,FONT_FOLDER,'-0.dds');await fs.writeFile(target,'PRESERVED FONT');
  await f.manager.install(f.game);
  const statePath=path.join(f.game,'.kh2fm-arabic/state.json'),state=await readJSON(statePath);state.version=version;
  for(const entry of state.entries.filter(x=>x.root==='mod')) {
    const previous=f.catalog.versions.find(x=>x.version===version).files.find(x=>x.path===entry.path);
    await fs.writeFile(path.join(state.modRoot,entry.path),version+':'+entry.path);entry.sha256=previous.sha256;entry.size=previous.size;
  }
  await writeJSON(statePath,state);await f.manager.install(f.game);
  assert.equal(await exists(target),false);assert.equal((await readJSON(statePath)).fontConflicts.length,1);
  await f.manager.remove(f.game);assert.equal(await fs.readFile(target,'utf8'),'PRESERVED FONT');
}));

for(const platform of ['win32','linux']) test(platform+': conflicting font images are saved, disabled, retained across reinstall, and restored on removal',async()=>withFixture(platform,async f=>{
  const old=await legacy(f),folder=path.join(old.mod,FONT_FOLDER);
  for(const name of ['-0.DDS','old.png','nested/1.dds']) {
    const target=path.join(folder,name);await fs.mkdir(path.dirname(target),{recursive:true});await fs.writeFile(target,'ORIGINAL:'+name);
  }
  assert.equal((await f.manager.inspect(f.game)).fontCheck.extraImages.length,3);
  await f.manager.install(f.game);
  let state=await readJSON(path.join(f.game,'.kh2fm-arabic/state.json'));
  assert.equal(state.fontConflicts.length,3);
  for(const entry of state.fontConflicts) assert.equal(await exists(path.join(old.mod,entry.path)),false);
  assert.deepEqual((await f.manager.inspect(f.game)).fontCheck.issues,[]);
  await f.manager.install(f.game);
  state=await readJSON(path.join(f.game,'.kh2fm-arabic/state.json'));
  assert.equal(state.fontConflicts.length,3);
  await f.manager.remove(f.game);
  for(const name of ['-0.DDS','old.png','nested/1.dds']) assert.equal(await fs.readFile(path.join(folder,name),'utf8'),'ORIGINAL:'+name);
  assert.equal(await exists(path.join(f.game,platform==='win32'?'DBGHELP.dll':'version.dll')),true);
  await f.manager.undo(f.game);
  for(const entry of state.fontConflicts) assert.equal(await exists(path.join(old.mod,entry.path)),false);
  assert.deepEqual((await f.manager.inspect(f.game)).fontCheck.issues,[]);
}));
test('font conflict repair can be undone and rolls back on a copying failure',async()=>withFixture('win32',async f=>{
  const old=await legacy(f),target=path.join(old.mod,FONT_FOLDER,'-0.dds');await fs.writeFile(target,'ORIGINAL DDS');
  await assert.rejects(f.manager.install(f.game,{afterWrite:()=>{throw new Error('disk failure');}}),/disk failure/);
  assert.equal(await fs.readFile(target,'utf8'),'ORIGINAL DDS');
  await f.manager.install(f.game);await f.manager.undo(f.game);
  assert.equal(await fs.readFile(target,'utf8'),'ORIGINAL DDS');
  for(const relative of f.payload) assert.equal(await fs.readFile(path.join(old.mod,relative),'utf8'),'1.0.1:'+relative);
}));
test('a modified saved conflicting font and a newly reintroduced font are protected',async()=>withFixture('win32',async f=>{
  const old=await legacy(f),target=path.join(old.mod,FONT_FOLDER,'-0.dds');await fs.writeFile(target,'ORIGINAL DDS');
  await f.manager.install(f.game);
  await fs.writeFile(target,'MY NEW FONT');
  await assert.rejects(f.manager.install(f.game),/تغيرت صورة خط/);
  await assert.rejects(f.manager.remove(f.game),/أضيفت صورة خط/);
  assert.equal(await fs.readFile(target,'utf8'),'MY NEW FONT');
  await fs.rm(target);
  const state=await readJSON(path.join(f.game,'.kh2fm-arabic/state.json'));
  await fs.writeFile(path.join(f.game,'.kh2fm-arabic',state.fontConflicts[0].original.path),'DAMAGED');
  await assert.rejects(f.manager.install(f.game),/النسخة الأصلية لصورة الخط/);
  await assert.rejects(f.manager.remove(f.game),/النسخة الأصلية لصورة الخط/);
}));
test('an external active mod path change is reported and blocked before copying',async()=>withFixture('win32',async f=>{
  const old=await legacy(f);await fs.rm(path.join(old.app,'kh2ar_state.txt'));
  await f.manager.install(f.game);
  const target=path.join(old.mod,f.payload[0]),before=await hash(target);
  await fs.writeFile(path.join(f.game,'panacea_settings.txt'),'mod_path=other\n');
  const check=(await f.manager.inspect(f.game)).fontCheck;
  assert.ok(check.issues.some(x=>x.includes('مجلد مودات مختلف')));
  await assert.rejects(f.manager.install(f.game),/مجلد مودات مختلف/);
  assert.equal(await hash(target),before);
  assert.equal(await fs.readFile(path.join(f.game,'panacea_settings.txt'),'utf8'),'mod_path=other\n');
}));
test('an external development font override is reported and preserved',async()=>withFixture('win32',async f=>{
  const old=await legacy(f);await fs.rm(path.join(old.app,'kh2ar_state.txt'));
  const dev=path.join(f.game,'dev',FONT_FOLDER);await fs.mkdir(dev,{recursive:true});await fs.writeFile(path.join(dev,'-0.dds'),'DEV FONT');
  await fs.appendFile(path.join(f.game,'panacea_settings.txt'),'dev_path=dev\n');
  assert.ok((await f.manager.inspect(f.game)).fontCheck.issues.some(x=>x.includes('مجلد التطوير')));
  await assert.rejects(f.manager.install(f.game),/مجلد التطوير/);
  assert.equal(await fs.readFile(path.join(dev,'-0.dds'),'utf8'),'DEV FONT');
}));
test('inspection detects damaged installed fonts and a forged conflict record cannot target messages',async()=>withFixture('win32',async f=>{
  await f.manager.install(f.game);
  const statePath=path.join(f.game,'.kh2fm-arabic/state.json'),state=await readJSON(statePath);
  await fs.writeFile(path.join(state.modRoot,'kh2/msg/us/fontimage.bar'),'CHANGED');
  assert.ok((await f.manager.inspect(f.game)).fontCheck.issues.some(x=>x.includes('لا تطابق')));
  state.fontConflicts=[{path:'kh2/msg/us/sys.bar',original:{path:'originals/'+ 'a'.repeat(32)+'.bin',sha256:'a'.repeat(64)}}];
  await writeJSON(statePath,state);
  await assert.rejects(f.manager.remove(f.game),/سجل تعارض الخط/);
}));

async function withFixture(platform,body) { const f=await fixture(platform); try { await body(f); } finally { await f.cleanup(); } }
async function previousManagerInstall(f,version) {
  const catalogVersion=version==='1.0.3'?'1.0.2':version;
  await f.manager.install(f.game);
  const file=path.join(f.game,'.kh2fm-arabic','state.json');
  const state=await readJSON(file); state.version=version;
  for(const entry of state.entries.filter(x=>x.root==='mod')) {
    const previous=f.catalog.versions.find(v=>v.version===catalogVersion).files.find(x=>x.path===entry.path);
    const bytes=Buffer.from(catalogVersion+':'+entry.path);
    await fs.writeFile(path.join(state.modRoot,...entry.path.split('/')),bytes);
    entry.sha256=previous.sha256;entry.size=bytes.length;
  }
  await writeJSON(file,state);
  return state;
}
for(const version of ['1.0.3','1.0.4','1.0.5','1.0.6','1.0.7','1.0.8','1.0.9','1.0.10','1.0.11','1.0.12']) for(const platform of ['win32','linux','darwin']) {
  test(platform+': upgrade '+version+' with changed font bytes, undo, and remove',async()=>withFixture(platform,async f=>{
    const previous=await previousManagerInstall(f,version);
    assert.equal((await f.manager.inspect(f.game)).version,version);
    await f.manager.install(f.game);
    assert.equal((await f.manager.inspect(f.game)).version,'1.0.13');
    for(const p of f.payload) assert.equal(await fs.readFile(path.join(previous.modRoot,...p.split('/')),'utf8'),'1.0.13:'+p);
    await f.manager.undo(f.game);
    assert.equal((await f.manager.inspect(f.game)).version,version);
    for(const p of f.payload) assert.equal(await fs.readFile(path.join(previous.modRoot,...p.split('/')),'utf8'),(version==='1.0.3'?'1.0.2':version)+':'+p);
    await f.manager.remove(f.game);
    for(const p of f.payload) assert.equal(await exists(path.join(previous.modRoot,...p.split('/'))),false);
    assert.equal(await fs.readFile(path.join(f.game,'save.dat'),'utf8'),'KEEP MY SAVE');
  }));
}
for(const version of ['1.0.3','1.0.6','1.0.7']) test('a forged '+version+' state cannot claim the new 1.0.13 file hashes',async()=>withFixture('win32',async f=>{
  await f.manager.install(f.game);
  const file=path.join(f.game,'.kh2fm-arabic','state.json');
  const state=await readJSON(file);state.version=version;await writeJSON(file,state);
  const before=await hash(path.join(state.modRoot,...f.payload[0].split('/')));
  await assert.rejects(f.manager.install(f.game),/غير مسموح/);
  assert.equal(await hash(path.join(state.modRoot,...f.payload[0].split('/'))),before);
}));
for (const platform of ['win32','linux','darwin']) {
  test(platform+': install, remove and undo preserve the game and saves',async()=>withFixture(platform,async f=>{
    const exe=await hash(path.join(f.game,GAME_EXE)); const save=await hash(path.join(f.game,'save.dat'));
    await f.manager.install(f.game);
    const state=await readJSON(path.join(f.game,'.kh2fm-arabic','state.json'));
    assert.equal((await f.manager.inspect(f.game)).version,'1.0.13');
    for (const entry of state.entries) assert.equal(await hash(path.join(entry.root==='mod' ? state.modRoot : f.game,...entry.path.split('/'))),entry.sha256);
    if (platform!=='win32') assert.equal(registryValue(await fs.readFile(path.join(f.prefix,'user.reg'),'utf8')),REG_LINE);
    await f.manager.remove(f.game); assert.equal((await f.manager.inspect(f.game)).installed,false);
    assert.equal(await exists(path.join(f.game,platform==='win32'?'DBGHELP.dll':'version.dll')),false);
    await f.manager.undo(f.game); assert.equal((await f.manager.inspect(f.game)).version,'1.0.13');
    assert.equal(await hash(path.join(f.game,GAME_EXE)),exe); assert.equal(await hash(path.join(f.game,'save.dat')),save);
  }));
}
test('upgrade 1.0.1 then remove does not restore the old Arabic translation',async()=>withFixture('win32',async f=>{
  const old=await legacy(f); await f.manager.install(f.game); await f.manager.remove(f.game);
  for (const p of f.payload) assert.equal(await exists(path.join(old.mod,...p.split('/'))),false);
  await f.manager.undo(f.game); assert.equal((await f.manager.inspect(f.game)).version,'1.0.13');
}));
test('undo an upgrade restores every old Arabic byte',async()=>withFixture('win32',async f=>{
  const old=await legacy(f); await f.manager.install(f.game); await f.manager.undo(f.game);
  for (const p of f.payload) assert.equal(await fs.readFile(path.join(old.mod,...p.split('/')),'utf8'),'1.0.1:'+p);
  assert.equal((await f.manager.inspect(f.game)).version,'1.0.1');
}));
test('remove an existing 1.0.2 installation directly and undo it',async()=>withFixture('win32',async f=>{
  const old=await legacy(f,'1.0.2'); await f.manager.remove(f.game);
  assert.equal(await exists(path.join(old.mod,...f.payload[0].split('/'))),false);
  await f.manager.undo(f.game); assert.equal((await f.manager.inspect(f.game)).version,'1.0.2');
}));
test('a legacy backup containing Arabic is not treated as the original game',async()=>withFixture('win32',async f=>{
  const old=await legacy(f); const target=path.join(old.mod,...f.payload[0].split('/'));
  await fs.writeFile(target+'.kh2ar.bak','1.0.2:'+f.payload[0]);
  await fs.writeFile(path.join(old.app,'kh2ar_backups.txt'),target+'\n');
  await f.manager.install(f.game); await f.manager.remove(f.game); assert.equal(await exists(target),false);
}));
test('an actual earlier mod backup is restored and its loader is preserved',async()=>withFixture('win32',async f=>{
  const old=await legacy(f); const target=path.join(old.mod,...f.payload[0].split('/'));
  await fs.writeFile(target+'.kh2ar.bak','ORIGINAL OTHER MOD');
  await fs.writeFile(path.join(old.app,'kh2ar_backups.txt'),target+'\n');
  await f.manager.install(f.game); await f.manager.remove(f.game);
  assert.equal(await fs.readFile(target,'utf8'),'ORIGINAL OTHER MOD');
  assert.equal(await exists(path.join(f.game,'DBGHELP.dll')),true);
}));
test('a loader used by a KH1 mod survives removing the KH2 translation',async()=>withFixture('win32',async f=>{
  const old=await legacy(f); const other=path.join(old.mod,'kh1','other.bar');
  await fs.mkdir(path.dirname(other),{recursive:true}); await fs.writeFile(other,'OTHER GAME MOD');
  await f.manager.install(f.game); await f.manager.remove(f.game);
  assert.equal(await fs.readFile(other,'utf8'),'OTHER GAME MOD'); assert.equal(await exists(path.join(f.game,'DBGHELP.dll')),true);
}));
test('damaged package is rejected before writing any game file',async()=>withFixture('win32',async f=>{
  await fs.appendFile(path.join(f.dataDir,'payload.bin'),'DAMAGED');
  await assert.rejects(f.manager.install(f.game),/حزمة التعريب/);
  assert.equal(await exists(path.join(f.game,'DBGHELP.dll')),false);
}));
test('late reinstall failure restores the entire preceding installation',async()=>withFixture('win32',async f=>{
  await f.manager.install(f.game); const before=await fs.readFile(path.join(f.game,'.kh2fm-arabic','state.json'));
  await assert.rejects(f.manager.install(f.game,{afterWrite:()=>{throw new Error('simulated disk failure');}}),/simulated disk failure/);
  assert.deepEqual(await fs.readFile(path.join(f.game,'.kh2fm-arabic','state.json')),before);
  assert.equal((await f.manager.inspect(f.game)).version,'1.0.13');
}));
test('cancel during copying restores the previous version',async()=>withFixture('win32',async f=>{
  const old=await legacy(f); let cancel=false;
  await assert.rejects(f.manager.install(f.game,{checkCancel:()=>{if(cancel) throw new Error('cancelled');},afterWrite:()=>{cancel=true;}}),/cancelled/);
  for (const p of f.payload) assert.equal(await fs.readFile(path.join(old.mod,...p.split('/')),'utf8'),'1.0.1:'+p);
}));
test('changed installed translation is protected during removal',async()=>withFixture('win32',async f=>{
  await f.manager.install(f.game); const state=await readJSON(path.join(f.game,'.kh2fm-arabic','state.json'));
  const target=path.join(state.modRoot,...f.payload[0].split('/')); await fs.writeFile(target,'MY EDITS');
  await assert.rejects(f.manager.remove(f.game),/تغيّر ملف/);
  assert.equal(await fs.readFile(target,'utf8'),'MY EDITS'); assert.equal(await exists(path.join(f.game,'DBGHELP.dll')),true);
}));
test('an unknown loader is protected',async()=>withFixture('win32',async f=>{
  await fs.writeFile(path.join(f.game,'DBGHELP.dll'),'OTHER LOADER');
  await assert.rejects(f.manager.install(f.game),/محمل مودات مختلف/);
  assert.equal(await fs.readFile(path.join(f.game,'DBGHELP.dll'),'utf8'),'OTHER LOADER');
}));
test('invalid game selection is rejected without creating metadata',async()=>withFixture('win32',async f=>{
  await assert.rejects(f.manager.install(f.root),/لا يحتوي/);
  assert.equal(await exists(path.join(f.root,'.kh2fm-arabic')),false);
}));
test('symbolic link to an unrelated directory is rejected',async()=>withFixture('win32',async f=>{
  const old=await legacy(f); const outside=path.join(f.root,'outside'); await fs.mkdir(outside);
  const target=path.join(old.mod,'kh2','msg'); await fs.rm(target,{recursive:true});
  await fs.symlink(outside,target,process.platform==='win32' ? 'junction' : 'dir');
  await assert.rejects(f.manager.install(f.game),/رابط/);
  assert.deepEqual(await fs.readdir(outside),[]);
}));
test('Wine removal preserves unrelated new registry settings',async()=>withFixture('linux',async f=>{
  const reg=path.join(f.prefix,'user.reg');
  await fs.appendFile(reg,'\n['+REG_SECTION+']\n"version"="builtin"\n');
  await f.manager.install(f.game); await fs.appendFile(reg,'\n[UnrelatedSettings]\n"new"="keep"\n');
  await f.manager.remove(f.game); const text=await fs.readFile(reg,'utf8');
  assert.equal(registryValue(text),'"version"="builtin"'); assert.match(text,/"new"="keep"/); assert.match(text,/"other"="native"/);
}));
test('changed Wine override is protected during removal',async()=>withFixture('linux',async f=>{
  await f.manager.install(f.game); const reg=path.join(f.prefix,'user.reg');
  await fs.writeFile(reg,patchRegistry(await fs.readFile(reg,'utf8'),'"version"="builtin"'));
  await assert.rejects(f.manager.remove(f.game),/تغير إعداد/);
  assert.equal((await f.manager.inspect(f.game)).version,'1.0.13');
}));
test('a real interrupted child process can be recovered after restart',async()=>withFixture('win32',async f=>{
  const child=spawnSync(process.execPath,['-e',"const {Manager}=require(process.argv[1]);const options=JSON.parse(process.argv[2]);new Manager(options).install(process.argv[3],{afterWrite:()=>process.exit(77)}).catch(e=>{console.error(e);process.exit(1)})",path.resolve(__dirname,'../src/engine.cjs'),JSON.stringify(f.options),f.game],{encoding:'utf8'});
  assert.equal(child.status,77,child.stderr); assert.equal((await f.manager.inspect(f.game)).pendingRecovery,true);
  await f.manager.undo(f.game); assert.equal((await f.manager.inspect(f.game)).pendingRecovery,false);
  assert.equal(await exists(path.join(f.game,'DBGHELP.dll')),false);
}));
test('undo refuses to overwrite a file modified after a successful operation',async()=>withFixture('win32',async f=>{
  await f.manager.install(f.game); await fs.writeFile(path.join(f.game,'DBGHELP.dll'),'CHANGED AFTER INSTALL');
  await assert.rejects(f.manager.undo(f.game),/تغيّر ملف بعد العملية/);
  assert.equal(await fs.readFile(path.join(f.game,'DBGHELP.dll'),'utf8'),'CHANGED AFTER INSTALL');
}));
test('forged recovery record cannot target the game executable',async()=>withFixture('win32',async f=>{
  await f.manager.install(f.game); const history=path.join(f.game,'.kh2fm-arabic','operations');
  const directory=path.join(history,(await fs.readdir(history))[0]); const file=path.join(directory,'journal.json');
  const journal=await readJSON(file); journal.records[0].target=path.join(f.game,GAME_EXE); await writeJSON(file,journal);
  await assert.rejects(f.manager.undo(f.game),/غير مسموح/);
  assert.equal(await fs.readFile(path.join(f.game,GAME_EXE),'utf8'),'ORIGINAL GAME EXECUTABLE');
}));
test('the manually selected Steam library link resolves to its actual game directory',async()=>withFixture('win32',async f=>{
  const link=path.join(f.root,'game-link');await fs.symlink(f.game,link,process.platform==='win32'?'junction':'dir');
  await f.manager.install(link);const state=await readJSON(path.join(f.game,'.kh2fm-arabic','state.json'));
  assert.equal(state.gameDir,await fs.realpath(f.game));await f.manager.remove(link);
}));
test('Wine upgrade migrates the owned DBGHELP loader to version.dll and can undo it',async()=>withFixture('linux',async f=>{
  const old=await legacy(f);await f.manager.install(f.game);
  assert.equal(await exists(path.join(f.game,'DBGHELP.dll')),false);assert.equal(await exists(path.join(f.game,'version.dll')),true);
  await f.manager.undo(f.game);assert.equal(await exists(path.join(f.game,'DBGHELP.dll')),true);assert.equal(await exists(path.join(f.game,'version.dll')),false);
  assert.equal(await fs.readFile(path.join(old.mod,...f.payload[0].split('/')),'utf8'),'1.0.1:'+f.payload[0]);
}));
test('a modified state cannot redirect removal to another Wine prefix',async()=>withFixture('linux',async f=>{
  await f.manager.install(f.game);const file=path.join(f.game,'.kh2fm-arabic','state.json');const state=await readJSON(file);
  const other=path.join(f.root,'another-prefix');await fs.mkdir(other);const reg=path.join(other,'user.reg');await fs.writeFile(reg,'WINE REGISTRY Version 2\nKEEP THIS REGISTRY');
  state.registry.prefix=other;await writeJSON(file,state);await assert.rejects(f.manager.remove(f.game),/لا تطابق/);
  assert.equal(await fs.readFile(reg,'utf8'),'WINE REGISTRY Version 2\nKEEP THIS REGISTRY');
}));
