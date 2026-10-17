'use strict';
const {_electron:electron}=require('playwright');
const assert=require('node:assert/strict');
const {fixture}=require('./fixture.cjs');
const {fs,path,exists,hash,readJSON,safeJoin}=require('../src/paths.cjs');
const {GAME_EXE}=require('../src/compatibility.cjs');
const {spawnSync}=require('node:child_process');
const {crypto,hashBytes,writeJSON}=require('../src/paths.cjs');

(async()=>{
  const root=path.resolve(__dirname,'..'),dist=path.join(root,'dist'),output=path.join(root,'test-results');await fs.mkdir(output,{recursive:true});
  const entries=await fs.readdir(dist);
  let executable;
  if(process.platform==='win32') executable=path.join(dist,'win-unpacked','KH2FM Arabic.exe');
  else if(process.platform==='darwin') {
    const dir=entries.find(x=>process.arch==='arm64' ? x==='mac-arm64' : x==='mac');
    executable=path.join(dist,dir,'KH2FM Arabic.app','Contents','MacOS','KH2FM Arabic');
  }else executable=path.join(dist,entries.find(x=>x.startsWith('linux') && x.endsWith('unpacked')),'kh2fm-arabic-manager');
  const f=await fixture(process.platform);let application;
  try{
    application=await electron.launch({executablePath:executable,args:process.platform==='linux'?['--no-sandbox']:[],timeout:120000});
    application.process().stderr?.on('data',data=>process.stderr.write(data));
    const page=await application.firstWindow();await page.emulateMedia({reducedMotion:'reduce'});await page.waitForSelector('#choose-game');await page.evaluate(()=>document.fonts.ready);
    await application.evaluate(({dialog},game)=>{dialog.showOpenDialog=async()=>({canceled:false,filePaths:[game]});},f.game);
    await page.locator('#choose-game').click();await page.waitForFunction(()=>!document.getElementById('install').disabled);
    const gameHash=await hash(path.join(f.game,GAME_EXE));
    await page.screenshot({path:path.join(output,'PACKAGED-'+process.platform+'-'+process.arch+'.png')});
    await page.locator('#install').click();await page.waitForFunction(()=>!document.getElementById('progress-area').hidden || !document.getElementById('feedback').hidden);
    await page.waitForFunction(()=>document.getElementById('progress-area').hidden && !document.getElementById('feedback').hidden,null,{timeout:240000});
    assert.match(await page.locator('#feedback-title').textContent(),/جاهز/,await page.locator('#feedback-text').textContent());
    const state=await readJSON(path.join(f.game,'.kh2fm-arabic','state.json'));assert.equal(state.entries.filter(x=>x.root==='mod').length,798);
    for(const entry of state.entries) assert.equal(await hash(safeJoin(entry.root==='mod'?state.modRoot:f.game,entry.path)),entry.sha256);
    await page.locator('#menu-toggle').click();await page.screenshot({path:path.join(output,'PACKAGED-MENU-'+process.platform+'-'+process.arch+'.png')});
    await page.locator('#remove').click();await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('حذف'),null,{timeout:240000});
    for(const entry of state.entries.filter(x=>x.root==='mod'))assert.equal(await exists(safeJoin(state.modRoot,entry.path)),false);
    await page.locator('#menu-toggle').click();await page.locator('#undo').click();await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('الاستعادة'),null,{timeout:240000});
    for(const entry of state.entries)assert.equal(await hash(safeJoin(entry.root==='mod'?state.modRoot:f.game,entry.path)),entry.sha256);
    assert.equal(await hash(path.join(f.game,GAME_EXE)),gameHash);assert.equal(await fs.readFile(path.join(f.game,'save.dat'),'utf8'),'KEEP MY SAVE');
    const conflictingImage=safeJoin(state.modRoot,'kh2/remastered/msg/us/fontimage.bar/fixture-old-font.dds');
    await fs.writeFile(conflictingImage,'ORIGINAL CONFLICTING FONT');
    await page.locator('#install').click();
    await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('جاهز') && document.getElementById('progress-area').hidden,null,{timeout:240000});
    assert.equal(await exists(conflictingImage),false);
    const repaired=await readJSON(path.join(f.game,'.kh2fm-arabic/state.json'));
    assert.equal(repaired.fontConflicts.length,1);
    assert.equal(await fs.readFile(safeJoin(path.join(f.game,'.kh2fm-arabic'),repaired.fontConflicts[0].original.path),'utf8'),'ORIGINAL CONFLICTING FONT');
    await page.locator('#menu-toggle').click();await page.locator('#undo').click();
    await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('الاستعادة'),null,{timeout:240000});
    assert.equal(await fs.readFile(conflictingImage,'utf8'),'ORIGINAL CONFLICTING FONT');
    await fs.rm(conflictingImage);
    for(const entry of state.entries)assert.equal(await hash(safeJoin(entry.root==='mod'?state.modRoot:f.game,entry.path)),entry.sha256);
    let windowsWorkerTested=false;
    if(process.platform==='win32') {
      const jobDir=path.join(f.root,'job-'+crypto.randomUUID());await fs.mkdir(jobDir);
      const request=path.join(jobDir,'request.json');await writeJSON(request,{schema:1,game:f.game,operation:'remove',prefixOverride:null});
      const digest=hashBytes(await fs.readFile(request));
      const child=spawnSync(executable,['--manager-job='+request,'--manager-job-hash='+digest],{encoding:'utf8',timeout:240000});
      assert.equal(child.status,0,(child.stdout || '')+(child.stderr || ''));
      const result=await readJSON(path.join(jobDir,'result.json'));assert.equal(result.ok,true,JSON.stringify(result));
      assert.equal(await exists(path.join(f.game,'DBGHELP.dll')),false);windowsWorkerTested=true;
    }
    const report={platform:process.platform,arch:process.arch,packagedApplication:true,passed:true,actualPayloadFiles:798,allFilesSHA256Verified:true,manualFolderSelection:true,menuRemoval:true,menuUndo:true,fontConflictRepairAndUndo:true,windowsWorkerTested,interactiveUACTested:false,gameAndSavePreserved:true,fixtureGame:true,actualGamePlayTested:false};
    await fs.writeFile(path.join(output,'PACKAGED-'+process.platform+'-'+process.arch+'.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{if(application)await application.close();await f.cleanup();}
})().catch(e=>{console.error(e);process.exitCode=1;});
