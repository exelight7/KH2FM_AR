'use strict';
const {_electron:electron}=require('playwright');
const assert=require('node:assert/strict');
const {execFile}=require('node:child_process');
const {promisify}=require('node:util');
const {Readable}=require('node:stream');
const {pipeline}=require('node:stream/promises');
const fss=require('node:fs');
const {gunzipSync}=require('node:zlib');
const {createHash}=require('node:crypto');
const {fs,path,readJSON,writeJSON,exists,hash}=require('../src/paths.cjs');
const {updateServer}=require('./update-feed.cjs');
const exec=promisify(execFile);
async function exerciseWindowsSelfUpdate(f,dist,profile) {
  const version=require('../package.json').version;
  const installer=path.join(dist,'KH2FM-Arabic-'+version+'-Windows-x64.exe');
  const installDir=path.join(f.root,'installed-launcher');
  const executable=path.join(installDir,'KH2FM Arabic.exe');
  const preferences=path.join(profile,'manager-preferences.json'),stateFile=path.join(f.game,'.kh2fm-arabic/state.json');
  const state=await readJSON(stateFile);state.installedAt='2000-01-01T00:00:00.000Z';await writeJSON(stateFile,state);
  await writeJSON(preferences,{schema:1,gameDir:f.game,prefixOverride:null,pendingVersion:null});
  const server=await updateServer(installer,version);server.good();
  const quote=text=>"'"+text.replaceAll("'","''")+"'";
  let application;
  try {
    // Exercise the exact published launcher the user already has. Neither
    // its code nor its updater comparison version is modified for this test.
    const previousInstaller=path.join(f.root,'published-1.0.12.exe');
    const response=await fetch('https://github.com/exelight7/KH2FM_AR/releases/download/v1.0.12/01-KH2FM-Arabic-1.0.12-Windows-x64.exe');
    assert.equal(response.ok,true,'Published 1.0.12 installer unavailable');
    await pipeline(Readable.fromWeb(response.body),fss.createWriteStream(previousInstaller));
    assert.equal(await hash(previousInstaller),'523f50891b654078016718db66dbd7461d7fe8fc202ed4222caeca5899beadb1');
    await exec(previousInstaller,['/S','/D='+installDir],{timeout:120000,windowsHide:true});
    assert.equal(await exists(executable),true);
    const previousData=path.join(installDir,'resources/translation');
    const previousManifest=await readJSON(path.join(previousData,'manifest.json'));
    assert.equal(previousManifest.version,'1.0.12');
    const blob=await fs.readFile(path.join(previousData,'payload.bin'));
    assert.equal(createHash('sha256').update(blob).digest('hex'),previousManifest.blobHash);
    const oldState=structuredClone(state);oldState.version='1.0.12';
    for(const entry of oldState.entries.filter(x=>x.root==='mod')) {
      const source=previousManifest.files.find(x=>x.path===entry.path);
      const bytes=gunzipSync(blob.subarray(source.offset,source.offset+source.compressedSize));
      assert.equal(createHash('sha256').update(bytes).digest('hex'),source.sha256);
      await fs.writeFile(path.join(oldState.modRoot,entry.path),bytes);
      entry.sha256=source.sha256;entry.size=source.size;
    }
    await writeJSON(stateFile,oldState);
    application=await electron.launch({executablePath:executable,timeout:120000});
    assert.equal(await application.evaluate(({app})=>app.getVersion()),'1.0.12');
    const page=await application.firstWindow();await page.waitForFunction(game=>document.getElementById('game-path').textContent===game,f.game);
    await application.evaluate(async({app},{url,cache})=>{
      const {createRequire}=process.getBuiltinModule('module');const require=createRequire(app.getAppPath()+'/package.json');
      const updater=require('electron-updater').autoUpdater;
      Object.defineProperty(updater.app,'baseCachePath',{value:cache});
      updater.setFeedURL({provider:'generic',url});
    },{url:server.url,cache:path.join(f.root,'real-update-cache')});
    await page.locator('#launcher-update').click();
    await page.waitForFunction(()=>document.getElementById('update-action').textContent.startsWith('تنزيل الإصدار'),null,{timeout:60000});
    await page.locator('#update-action').click();
    await page.waitForFunction(()=>document.getElementById('update-action').textContent==='التحديث وإعادة التشغيل',null,{timeout:180000});
    const closed=application.waitForEvent('close',{timeout:120000});
    await page.locator('#update-action').click().catch(error=>{if(!error.message.includes('closed'))throw error;});
    await closed;application=null;
    const deadline=Date.now()+180000;let applied=false;
    while(Date.now()<deadline) {
      try {
        const current=await readJSON(stateFile),saved=await readJSON(preferences);
        if(current.version===version && current.installedAt!==state.installedAt && saved.gameDir===f.game && saved.pendingVersion===null){applied=true;break;}
      }catch{/* Atomic files may be in the middle of replacement. */}
      await new Promise(resolve=>setTimeout(resolve,300));
    }
    assert.equal(applied,true,'The silently updated launcher did not resume and apply the translation');
    assert.equal(await hash(executable),await hash(path.join(dist,'win-unpacked/KH2FM Arabic.exe')));
    for(const entry of state.entries)assert.equal(await hash(path.join(entry.root==='mod'?state.modRoot:f.game,entry.path)),entry.sha256);
    return {realSilentSelfUpdate:true,previousLauncherVersion:'1.0.12',previousPublishedInstallerSHA256Verified:true,
      updaterComparisonVersionUnmodified:true,newLauncherRelaunched:true,gameDirectoryRestored:true,translationAppliedAfterSelfUpdate:true};
  }finally {
    if(application)await application.close().catch(()=>{});
    // Only stop this test's installed executable, never other launchers.
    await exec('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -eq "+quote(executable)+" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"],{windowsHide:true}).catch(()=>{});
    const uninstaller=path.join(installDir,'Uninstall KH2FM Arabic.exe');
    if(await exists(uninstaller))await exec(uninstaller,['/S'],{timeout:120000,windowsHide:true});
    await server.close();
  }
}
module.exports={exerciseWindowsSelfUpdate};
