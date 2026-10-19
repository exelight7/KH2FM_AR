'use strict';
const {_electron:electron}=require('playwright');
const assert=require('node:assert/strict');
const {fixture}=require('./fixture.cjs');
const {fs,path,exists,hash}=require('../src/paths.cjs');
const {GAME_EXE}=require('../src/compatibility.cjs');

(async()=>{
  const root=path.resolve(__dirname,'..'); const output=path.join(root,'test-results'); await fs.mkdir(output,{recursive:true});
  const f=await fixture(process.platform);
  const loaderName=process.platform==='win32'?'DBGHELP.dll':'version.dll';
  const actualData=path.join(root,'data'); const savedData=path.join(root,'data-real');
  await fs.rename(actualData,savedData); await fs.cp(f.dataDir,actualData,{recursive:true});
  const catalog=path.join(root,'catalog','legacy.json'); const oldCatalog=await fs.readFile(catalog);
  await fs.writeFile(catalog,JSON.stringify(f.catalog));
  let application;
  const env={...process.env,LANG:'en_US.UTF-8',...(process.platform==='linux'?{XDG_CONFIG_HOME:path.join(f.root,'config'),XDG_CACHE_HOME:path.join(f.root,'cache')}:{})};
  try{
    application=await electron.launch({args:[root,...(process.platform==='linux'?['--no-sandbox']:[])],env,timeout:90000});
    const page=await application.firstWindow();await page.emulateMedia({reducedMotion:'reduce'}); const errors=[]; page.on('pageerror',e=>errors.push(e.message));
    await page.waitForSelector('#owner-art'); await page.evaluate(()=>document.fonts.ready);
    assert.equal(await page.locator('#install').isDisabled(),true);
    await application.evaluate(({dialog},game)=>{dialog.showOpenDialog=async()=>({canceled:false,filePaths:[game]});},f.game);
    const exe=await hash(path.join(f.game,GAME_EXE));
    await page.locator('#choose-game').click(); await page.waitForFunction(()=>!document.getElementById('install').disabled);
    await page.screenshot({path:path.join(output,'NATIVE-'+process.platform+'-'+process.arch+'.png')});
    await page.locator('#install').click(); await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('جاهز'),null,{timeout:90000});
    assert.equal(await exists(path.join(f.game,'.kh2fm-arabic','state.json')),true);
    await page.locator('#menu-toggle').click(); await page.screenshot({path:path.join(output,'NATIVE-MENU-'+process.platform+'-'+process.arch+'.png')});
    await page.locator('#font-report').click();
    await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('نُسخ'));
    const report=JSON.parse(await application.evaluate(({clipboard})=>clipboard.readText()));
    assert.deepEqual(report.fontCheck.issues,[]);
    assert.equal(report.fontCheck.files.length,5);
    assert.ok(report.fontCheck.files.every(x=>x.actual===x.expected));
    await page.locator('#menu-toggle').click();
    await page.locator('#remove').click(); await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('حذف'),null,{timeout:90000});
    assert.equal(await exists(path.join(f.game,loaderName)),false);
    await page.locator('#menu-toggle').click(); await page.locator('#undo').click(); await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('الاستعادة'),null,{timeout:90000});
    assert.equal(await exists(path.join(f.game,loaderName)),true); assert.equal(await hash(path.join(f.game,GAME_EXE)),exe);
    await application.close();
    application=await electron.launch({args:[root,...(process.platform==='linux'?['--no-sandbox']:[])],env,timeout:90000});
    const reopened=await application.firstWindow();
    await reopened.waitForFunction(game=>document.getElementById('game-path').textContent===game,f.game);
    assert.equal(await reopened.locator('#install').isEnabled(),true);
    assert.equal(errors.length,0,errors.join('\n'));
    await fs.writeFile(path.join(output,'NATIVE-'+process.platform+'-'+process.arch+'.json'),JSON.stringify({platform:process.platform,arch:process.arch,nativeElectron:true,passed:true,checks:['manualFolderSelection','originalArtwork','installFromButton','removeFromMenu','undoFromMenu','fontReportClipboardAndHashes','gameDirectoryRememberedAfterRestart','gameExePreserved','noJavaScriptErrors'],fixtureOnly:true},null,2)+'\n');
    console.log('Native Electron install/remove/undo passed on '+process.platform+'/'+process.arch);
  }finally{
    if(application)await application.close();
    await fs.rm(actualData,{recursive:true,force:true});await fs.rename(savedData,actualData);await fs.writeFile(catalog,oldCatalog);await f.cleanup();
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
