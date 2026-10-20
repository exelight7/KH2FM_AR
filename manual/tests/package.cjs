'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
const crypto=require('node:crypto');
const zlib=require('node:zlib');
const {spawn}=require('node:child_process');
const opts=Object.fromEntries(process.argv.slice(2).reduce((a,x,i,v)=>i%2===0?[...a,[x.slice(2),v[i+1]]]:a,[]));
const root=path.resolve(opts.package),game=path.resolve(opts.game),out=path.resolve(opts.output);
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const hash=async file=>digest(await fs.readFile(file));
const readJSON=async file=>JSON.parse(await fs.readFile(file,'utf8'));
const exeName='KINGDOM HEARTS II FINAL MIX.exe';
async function run(exe,args,environment={}){
  return await new Promise((resolve,reject)=>{
    const child=spawn(exe,args,{cwd:root,windowsHide:true,env:{...process.env,...environment}});let stdout='',stderr='';
    child.stdout.on('data',b=>{stdout+=b;});child.stderr.on('data',b=>{stderr+=b;});child.on('error',reject);
    const timer=setTimeout(()=>{child.kill();reject(Error('Test process timed out'));},600000);
    child.on('close',code=>{clearTimeout(timer);resolve({code,stdout,stderr});});
  });
}
(async()=>{
  await fs.mkdir(out,{recursive:false});
  const report={version:'2.0.1',edition:'Manual Edition',fixtureGame:true,actualGamePlayTested:false,tests:{}};
  async function pass(name,fn){await fn();report.tests[name]='PASS';console.log('PASS '+name);await fs.writeFile(path.join(out,'TEST_REPORT.json'),JSON.stringify(report,null,2)+'\n');}
  const manifest=await readJSON(path.join(root,'files/manual-manifest.json'));
  const official=await readJSON(path.join(root,'files/manifest.json'));
  const expected=new Map(official.files.map(f=>[f.path,f]));
  const actualState=path.join(game,'.kh2fm-arabic/state.json');
  const before={exe:await hash(path.join(game,exeName)),state:await hash(actualState),heds:{},pkgs:{}};
  for(const hed of Object.keys(manifest.heds)){
    before.heds[hed]=await hash(path.join(game,'Image/dt',hed));
    const s=await fs.stat(path.join(game,'Image/dt',hed.replace('.hed','.pkg')));before.pkgs[hed]={size:s.size,mtime:s.mtimeMs};
  }
  const fixture=path.join(out,'game'),user=path.join(out,'user');await fs.mkdir(path.join(fixture,'Image/dt'),{recursive:true});await fs.mkdir(user);
  await fs.copyFile(path.join(game,exeName),path.join(fixture,exeName));
  for(const hed of Object.keys(manifest.heds)){
    await fs.copyFile(path.join(game,'Image/dt',hed),path.join(fixture,'Image/dt',hed));
    await fs.writeFile(path.join(fixture,'Image/dt',hed.replace('.hed','.pkg')),'FIXTURE ARCHIVE NOT USED FOR PREPARATION');
  }
  await fs.writeFile(path.join(fixture,'save.dat'),'KEEP SAVE');
  await fs.writeFile(path.join(fixture,'steam-config-fixture.txt'),'KEEP STEAM CONFIG');
  const node=path.join(root,'tools/node.exe'),cli=path.join(root,'scripts/manual.cjs'),helper=path.join(root,'tools/ManualAssets.exe');
  // Only the isolated fixture's process-list dependency is mocked. No game is launched.
  const fixtureRunner="const cp=require('node:child_process');const original=cp.execFileSync;cp.execFileSync=(exe,args,options)=>exe==='tasklist.exe'?'':original(exe,args,options);require(process.argv[1]).main(process.argv.slice(2)).catch(e=>{console.error('ERROR: '+e.message);process.exitCode=1;});";
  report.fixtureGameProcessListMocked=true;
  const command=(operation,selected=fixture)=>run(node,['-e',fixtureRunner,cli,operation,'--game',selected],{LOCALAPPDATA:user});
  await pass('portableRuntimeAndPackageIntegrity',async()=>{
    let r=await command('check');assert.equal(r.code,0,r.stderr);assert.match(r.stdout,/PASS/);
    r=await run(helper,['--self-test']);assert.equal(r.code,0,r.stderr);
  });
  const data=path.join(out,'prepared');
  await pass('realArchiveReadAndExact846FileReconstruction',async()=>{
    const r=await run(helper,['prepare',path.join(root,'files/manual-manifest.json'),game,data]);assert.equal(r.code,0,r.stderr);
    await fs.writeFile(path.join(out,'PREPARE_LOG.txt'),r.stdout+r.stderr);
    const m=await readJSON(path.join(data,'manifest.json')),blob=await fs.readFile(path.join(data,'payload.bin'));
    assert.equal(digest(blob),m.blobHash);assert.equal(m.files.length,846);
    for(const entry of m.files){
      const original=expected.get(entry.path);assert(original);assert.equal(entry.sha256,original.sha256);assert.equal(entry.size,original.size);
      const bytes=zlib.gunzipSync(blob.subarray(entry.offset,entry.offset+entry.compressedSize));assert.equal(digest(bytes),original.sha256);
    }
    assert.equal(m.files.filter(f=>f.group==='payload').length,831);
  });
  const cache=path.join(user,'KH2FM-Arabic/manual-cache',digest(Buffer.from(fixture.toLowerCase())).slice(0,20),'2.0.1');
  await fs.mkdir(cache,{recursive:true});await fs.copyFile(path.join(data,'manifest.json'),path.join(cache,'manifest.json'));await fs.copyFile(path.join(data,'payload.bin'),path.join(cache,'payload.bin'));
  const stateFile=path.join(fixture,'.kh2fm-arabic/state.json');
  let installed;
  await pass('cliInstallAndVerifyWithActual831Files',async()=>{
    let r=await command('install');assert.equal(r.code,0,r.stderr);installed=await readJSON(stateFile);assert.equal(installed.version,'2.0.1');
    assert.equal(installed.entries.filter(e=>e.root==='mod').length,831);
    for(const entry of installed.entries)assert.equal(await hash(path.join(entry.root==='mod'?installed.modRoot:fixture,entry.path)),entry.sha256);
    r=await command('verify');assert.equal(r.code,0,r.stderr);
  });
  const other=path.join(installed.modRoot,'kh2/unrelated-mod.txt');await fs.writeFile(other,'KEEP OTHER MOD');
  await pass('cliRemovalPreservesOtherModsSaveSteamAndBackups',async()=>{
    const r=await command('remove');assert.equal(r.code,0,r.stderr);
    for(const entry of installed.entries.filter(e=>e.root==='mod'))await assert.rejects(fs.access(path.join(installed.modRoot,entry.path)));
    assert.equal(await fs.readFile(other,'utf8'),'KEEP OTHER MOD');assert.equal(await fs.readFile(path.join(fixture,'save.dat'),'utf8'),'KEEP SAVE');
    assert.equal(await fs.readFile(path.join(fixture,'steam-config-fixture.txt'),'utf8'),'KEEP STEAM CONFIG');
    assert((await fs.readdir(path.join(fixture,'.kh2fm-arabic/operations'))).length>=2);
  });
  await pass('cliUndoRestoresExactInstallation',async()=>{
    const r=await command('undo');assert.equal(r.code,0,r.stderr);
    for(const entry of installed.entries)assert.equal(await hash(path.join(entry.root==='mod'?installed.modRoot:fixture,entry.path)),entry.sha256);
  });
  await pass('real2.0.0StateUpgradeAndUndo',async()=>{
    const old=structuredClone(installed);old.version='2.0.0';old.entries=old.entries.filter(e=>e.path!=='kh2/dll/KH2FM_AR_GreenCommandText.dll');
    await fs.unlink(path.join(old.modRoot,'kh2/dll/KH2FM_AR_GreenCommandText.dll'));await fs.writeFile(stateFile,JSON.stringify(old,null,2)+'\n');
    let r=await command('install');assert.equal(r.code,0,r.stderr);assert.equal((await readJSON(stateFile)).version,'2.0.1');
    r=await command('undo');assert.equal(r.code,0,r.stderr);assert.equal((await readJSON(stateFile)).version,'2.0.0');
    r=await command('install');assert.equal(r.code,0,r.stderr);
  });
  await pass('modifiedManagedFileRefusedWithoutLoss',async()=>{
    const file=path.join(installed.modRoot,'kh2/dll/KH2FM_AR_GreenCommandText.dll'),before=await fs.readFile(file);
    try{await fs.writeFile(file,'USER EDIT');const r=await command('remove');assert.notEqual(r.code,0);assert.equal(await fs.readFile(file,'utf8'),'USER EDIT');}finally{await fs.writeFile(file,before);}
  });
  await pass('unknownExecutableAndChangedIndexRefused',async()=>{
    const file=path.join(fixture,exeName),before=await fs.readFile(file);
    try{await fs.writeFile(file,'UNKNOWN VERSION');const r=await command('install');assert.notEqual(r.code,0);assert.match(r.stderr,/Unsupported or unknown/);}finally{await fs.writeFile(file,before);}
    const hed=path.join(fixture,'Image/dt',Object.keys(manifest.heds)[0]),original=await fs.readFile(hed);
    try{await fs.appendFile(hed,'CHANGED');const r=await command('install');assert.notEqual(r.code,0);assert.match(r.stderr,/Unsupported or changed/);}finally{await fs.writeFile(hed,original);}
  });
  await pass('damagedDistributedPatchRefused',async()=>{
    const entry=manifest.files.find(e=>e.container),file=path.join(root,'files',entry.file),before=await fs.readFile(file);
    try{const altered=Buffer.from(before);altered[10]^=1;await fs.writeFile(file,altered);const r=await command('check');assert.notEqual(r.code,0);assert.match(r.stderr,/Damaged package/);}finally{await fs.writeFile(file,before);}
  });
  await pass('wrongOriginalHashRefusedBeforeInstall',async()=>{
    const altered=structuredClone(manifest);altered.files.find(e=>e.container).sourceHash='0'.repeat(64);
    const file=path.join(root,'files/test-bad-manifest.json');
    try{await fs.writeFile(file,JSON.stringify(altered));const output=path.join(out,'rejected-preparation');const r=await run(helper,['prepare',file,game,output]);assert.notEqual(r.code,0);assert.match(r.stderr,/Original data hash mismatch/);await assert.rejects(fs.access(path.join(output,'manifest.json')));}finally{await fs.unlink(file);}
  });
  await pass('actualGameExeIndicesInstalledStateAndArchiveMetadataUnchanged',async()=>{
    assert.equal(await hash(path.join(game,exeName)),before.exe);assert.equal(await hash(actualState),before.state);
    for(const hed of Object.keys(manifest.heds)){
      assert.equal(await hash(path.join(game,'Image/dt',hed)),before.heds[hed]);
      const s=await fs.stat(path.join(game,'Image/dt',hed.replace('.hed','.pkg')));assert.deepEqual({size:s.size,mtime:s.mtimeMs},before.pkgs[hed]);
    }
  });
  report.passed=true;await fs.writeFile(path.join(out,'TEST_REPORT.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
})().catch(error=>{console.error(error);process.exitCode=1;});
