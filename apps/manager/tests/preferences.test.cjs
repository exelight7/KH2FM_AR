'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const os=require('node:os');
const {fs,path}=require('../src/paths.cjs');
const {loadPreferences,savePreferences}=require('../src/preferences.cjs');
test('remember the game directory, Wine prefix and pending update across restarts',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'kh2-preferences-'));
  try {
    const file=path.join(root,'preferences.json'),value={gameDir:path.join(root,'Game'),prefixOverride:path.join(root,'Wine'),pendingVersion:'1.0.14'};
    assert.deepEqual(await loadPreferences(file),{});await savePreferences(file,value);
    assert.deepEqual(await loadPreferences(file),value);
  }finally{await fs.rm(root,{recursive:true,force:true});}
});
test('invalid saved settings are ignored instead of breaking launcher startup',async()=>{
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'kh2-preferences-'));
  try {
    const file=path.join(root,'preferences.json');
    for(const invalid of ['broken json','null','[]',JSON.stringify({schema:1,gameDir:'relative',prefixOverride:null}),JSON.stringify({schema:1,gameDir:path.join(root,'Game'),prefixOverride:'relative'})]) {
      await fs.writeFile(file,invalid);assert.deepEqual(await loadPreferences(file),{});
    }
  }finally{await fs.rm(root,{recursive:true,force:true});}
});
