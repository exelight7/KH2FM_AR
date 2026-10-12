'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {fs,path,hash,hashBytes,readJSON,writeJSON,exists}=require('../src/paths.cjs');
const {REG_LINE,REG_SECTION,registryValue,patchRegistry,GAME_EXE}=require('../src/compatibility.cjs');
const {fixture,legacy}=require('./fixture.cjs');

async function withFixture(platform,body) { const f=await fixture(platform); try { await body(f); } finally { await f.cleanup(); } }
for (const platform of ['win32','linux','darwin']) {
  test(platform+': install, remove and undo preserve the game and saves',async()=>withFixture(platform,async f=>{
    const exe=await hash(path.join(f.game,GAME_EXE)); const save=await hash(path.join(f.game,'save.dat'));
    await f.manager.install(f.game);
    const state=await readJSON(path.join(f.game,'.kh2fm-arabic','state.json'));
    assert.equal((await f.manager.inspect(f.game)).version,'1.0.3');
    for (const entry of state.entries) assert.equal(await hash(path.join(entry.root==='mod' ? state.modRoot : f.game,...entry.path.split('/'))),entry.sha256);
    if (platform!=='win32') assert.equal(registryValue(await fs.readFile(path.join(f.prefix,'user.reg'),'utf8')),REG_LINE);
    await f.manager.remove(f.game); assert.equal((await f.manager.inspect(f.game)).installed,false);
    assert.equal(await exists(path.join(f.game,platform==='win32'?'DBGHELP.dll':'version.dll')),false);
    await f.manager.undo(f.game); assert.equal((await f.manager.inspect(f.game)).version,'1.0.3');
    assert.equal(await hash(path.join(f.game,GAME_EXE)),exe); assert.equal(await hash(path.join(f.game,'save.dat')),save);
  }));
}
test('upgrade 1.0.1 then remove does not restore the old Arabic translation',async()=>withFixture('win32',async f=>{
  const old=await legacy(f); await f.manager.install(f.game); await f.manager.remove(f.game);
  for (const p of f.payload) assert.equal(await exists(path.join(old.mod,...p.split('/'))),false);
  await f.manager.undo(f.game); assert.equal((await f.manager.inspect(f.game)).version,'1.0.3');
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
  await assert.rejects(f.manager.install(f.game,{afterWrite:i=>{if(i===3) throw new Error('simulated disk failure');}}),/simulated disk failure/);
  assert.deepEqual(await fs.readFile(path.join(f.game,'.kh2fm-arabic','state.json')),before);
  assert.equal((await f.manager.inspect(f.game)).version,'1.0.3');
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
  assert.equal((await f.manager.inspect(f.game)).version,'1.0.3');
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
