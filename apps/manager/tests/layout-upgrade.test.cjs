'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {gzipSync}=require('node:zlib');
const {fixture}=require('./fixture.cjs');
const {Manager}=require('../src/engine.cjs');
const {fs,path,readJSON,writeJSON,hashBytes,exists}=require('../src/paths.cjs');

for(const platform of ['win32','linux']) test(platform+': new command layout survives upgrade, undo and removal',async()=>{
  const f=await fixture(platform),relative='kh2/field2d/us/bb0command.2dd';
  try {
    await f.manager.install(f.game);
    const old=await readJSON(path.join(f.dataDir,'manifest.json'));
    const stateFile=path.join(f.game,'.kh2fm-arabic/state.json'),before=await readJSON(stateFile);
    before.version='1.0.19';await writeJSON(stateFile,before);
    f.catalog.versions.find(x=>x.version==='1.0.19').files=old.files.filter(x=>x.group==='payload');
    const bytes=Buffer.from('GREEN TEXT Y ONLY'),compressed=gzipSync(bytes);
    const blob=await fs.readFile(path.join(f.dataDir,'payload.bin'));
    const next=Buffer.concat([blob,compressed]);
    await fs.writeFile(path.join(f.dataDir,'payload.bin'),next);
    await writeJSON(path.join(f.dataDir,'manifest.json'),{...old,version:'1.0.20',blobHash:hashBytes(next),files:[...old.files,
      {path:relative,group:'payload',size:bytes.length,sha256:hashBytes(bytes),offset:blob.length,compressedSize:compressed.length}]});
    const current=await readJSON(path.join(f.dataDir,'manifest.json'));
    f.catalog.versions.push({version:'1.0.20',files:current.files.filter(x=>x.group==='payload')});
    const manager=new Manager(f.options);
    await manager.install(f.game);
    const state=await readJSON(path.join(f.game,'.kh2fm-arabic/state.json')),target=path.join(state.modRoot,relative);
    assert.equal(state.version,'1.0.20');assert.deepEqual(await fs.readFile(target),bytes);
    await manager.undo(f.game);
    assert.equal(await exists(target),false);assert.equal((await manager.inspect(f.game)).version,'1.0.19');
    await manager.install(f.game);
    await manager.remove(f.game);assert.equal(await exists(target),false);
    await manager.undo(f.game);assert.deepEqual(await fs.readFile(target),bytes);
    await fs.writeFile(target,'USER EDIT');
    await assert.rejects(manager.remove(f.game));
    assert.equal(await fs.readFile(target,'utf8'),'USER EDIT');
    assert.equal(await fs.readFile(path.join(f.game,'save.dat'),'utf8'),'KEEP MY SAVE');
  }finally{await f.cleanup();}
});
