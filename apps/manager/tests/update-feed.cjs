'use strict';
const assert=require('node:assert/strict');
const http=require('node:http');
const fss=require('node:fs');
const {createHash}=require('node:crypto');
const {fs,path,readJSON,exists}=require('../src/paths.cjs');
async function sha512(file) {
  const hash=createHash('sha512');for await(const chunk of fss.createReadStream(file))hash.update(chunk);return hash.digest('base64');
}
async function updateServer(binary,version='999.0.0') {
  const size=(await fs.stat(binary)).size,digest=await sha512(binary),name='verified-update'+(process.platform==='win32'?'.exe':'.AppImage');
  let damaged=true;
  const server=http.createServer((req,res)=>{
    const pathname=new URL(req.url,'http://localhost').pathname;
    if(['/latest.yml','/latest-linux.yml'].includes(pathname)) {
      const hash=damaged?Buffer.alloc(64).toString('base64'):digest;
      res.setHeader('Content-Type','application/yaml');res.end(JSON.stringify({version,files:[{url:name,sha512:hash,size}],path:name,sha512:hash,releaseDate:new Date().toISOString()}));
    }else if(pathname==='/'+name) {
      res.setHeader('Content-Length',String(size));res.setHeader('Content-Type','application/octet-stream');fss.createReadStream(binary).pipe(res);
    }else{res.writeHead(404);res.end();}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  return {url:'http://127.0.0.1:'+server.address().port+'/',digest,good:()=>{damaged=false;},close:()=>new Promise(resolve=>server.close(resolve))};
}
async function configure(application,url,cacheDir) {
  await application.evaluate(async({app},{url,cacheDir})=>{
    const {createRequire}=process.getBuiltinModule('module');const require=createRequire(app.getAppPath()+'/package.json');
    const {autoUpdater}=require('electron-updater');
    Object.defineProperty(autoUpdater.app,'baseCachePath',{value:cacheDir});
    autoUpdater.setFeedURL({provider:'generic',url});
    autoUpdater.quitAndInstall=(silent,force)=>{globalThis.testUpdateRestart={silent,force};};
  },{url,cacheDir});
}
async function exerciseUpdate(application,page,f,dist,executable) {
  const version=require('../package.json').version;
  const packaged=process.platform==='win32'?path.join(dist,'KH2FM-Arabic-'+version+'-Windows-x64.exe'):path.join(dist,'KH2FM-Arabic-'+version+'-Linux-x86_64.AppImage');
  const binary=await exists(packaged)?packaged:executable;
  const server=await updateServer(binary);
  try {
    await configure(application,server.url,path.join(f.root,'update-cache'));
    await page.locator('#launcher-update').click();
    await page.waitForFunction(()=>document.getElementById('update-action').textContent.includes('999.0.0'),null,{timeout:60000});
    await page.locator('#update-action').click();
    await page.waitForFunction(()=>document.getElementById('update-action').textContent==='إعادة المحاولة',null,{timeout:180000});
    assert.equal(await application.evaluate(()=>globalThis.testUpdateRestart || null),null);
    server.good();await page.locator('#update-action').click();
    await page.waitForFunction(()=>document.getElementById('update-action').textContent.includes('999.0.0'),null,{timeout:60000});
    await page.locator('#update-action').click();
    await page.waitForFunction(()=>document.getElementById('update-action').textContent==='التحديث وإعادة التشغيل',null,{timeout:180000});
    const cached=await application.evaluate(async({app})=>{
      const {createRequire}=process.getBuiltinModule('module');const require=createRequire(app.getAppPath()+'/package.json');
      return require('electron-updater').autoUpdater.downloadedUpdateHelper.file;
    });
    assert.equal(await sha512(cached),server.digest);
    await page.locator('#update-action').click();
    const restart=await application.evaluate(()=>new Promise((resolve,reject)=>{
      const deadline=Date.now()+10000;
      const timer=setInterval(()=>{if(globalThis.testUpdateRestart){clearInterval(timer);resolve(globalThis.testUpdateRestart);}else if(Date.now()>deadline){clearInterval(timer);reject(new Error('Restart was not requested'));}},50);
    }));
    assert.deepEqual(restart,{silent:true,force:true});
    const profile=await application.evaluate(({app})=>app.getPath('userData'));
    const preferences=await readJSON(path.join(profile,'manager-preferences.json'));
    assert.equal(preferences.gameDir,f.game);assert.equal(preferences.pendingVersion,'999.0.0');
    return {realUpdaterFeed:true,corruptSHA512Rejected:true,verifiedBinaryDownloaded:true,silentRestartRequested:true,restartExecutionMocked:true,gameSelectionPersisted:true};
  }finally{await server.close();}
}
module.exports={exerciseUpdate,updateServer,configure};
