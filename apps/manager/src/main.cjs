'use strict';
const {app,BrowserWindow,ipcMain,dialog,clipboard}=require('electron');
const path=require('node:path');
const {execFile}=require('node:child_process');
const {promisify}=require('node:util');
const {Manager}=require('./engine.cjs');
const {needsElevation,elevatedOperation,runWorker}=require('./windows-worker.cjs');
const fs=require('node:fs/promises');
const catalog=require('../catalog/legacy.json');
const exec=promisify(execFile);
let window,manager,selected=null,prefixOverride=null,busy=false,cancelled=false,closeAfter=false;
const respond=async callback=>{try{return {ok:true,value:await callback()};}catch(e){return {ok:false,error:e.message};}};
function trusted(event) { if (!window || event.sender!==window.webContents || event.senderFrame!==window.webContents.mainFrame) throw new Error('طلب غير مسموح.'); }
async function ensureGameClosed(prefix) {
  const executable='KINGDOM HEARTS II FINAL MIX.exe';
  if(process.platform==='win32') {
    const {stdout}=await exec('tasklist.exe',['/FI','IMAGENAME eq '+executable,'/FO','CSV','/NH'],{windowsHide:true});
    if(stdout.toLowerCase().includes('"'+executable.toLowerCase()+'"')) throw new Error('أغلق اللعبة قبل التثبيت أو الحذف.');
  } else {
    const {stdout}=await exec('ps',['-ax','-o','args=']);
    if(stdout.includes(executable)) throw new Error('أغلق اللعبة قبل التثبيت أو الحذف.');
    const wineProcess=/(?:^|[\s/])wine(?:server(?:64)?|64|32)?(?:-preloader)?(?:\s|$)/i;
    if(process.platform==='darwin' && stdout.split('\n').some(x=>wineProcess.test(x))) throw new Error('أغلق اللعبة وSteam داخل Wine أو CrossOver أثناء التثبيت أو الحذف، ثم افتحهما بعد الانتهاء.');
    if(process.platform==='linux' && prefix) {
      for(const pid of await fs.readdir('/proc')) {
        if(!/^\d+$/.test(pid)) continue;
        try {
          const command=await fs.readFile('/proc/'+pid+'/cmdline','utf8');
          if(!wineProcess.test(command.replaceAll('\0',' '))) continue;
          const environment=await fs.readFile('/proc/'+pid+'/environ','utf8');
          if(environment.split('\0').some(x=>x==='WINEPREFIX='+prefix)) throw new Error('أغلق اللعبة وبيئة Wine التابعة لها قبل التثبيت أو الحذف.');
        }catch(e){if(!['ENOENT','EACCES','ESRCH'].includes(e.code)) throw e;}
      }
    }
  }
}
function progress(message) { if(window && !window.isDestroyed()) window.webContents.send('manager:progress',message); }
app.setName('KH2FM Arabic');
const workerRequest=process.argv.find(x=>x.startsWith('--manager-job='));
if(workerRequest) {
  app.disableHardwareAcceleration();
  app.whenReady().then(async()=>{
    try{const hashArg=process.argv.find(x=>x.startsWith('--manager-job-hash='));const status=await runWorker(workerRequest.slice('--manager-job='.length),hashArg?.slice('--manager-job-hash='.length));app.exit(status);}
    catch(error){console.error(error);app.exit(1);}
  });
}else{
app.whenReady().then(()=>{
  const dataDir=app.isPackaged ? path.join(process.resourcesPath,'translation') : path.resolve(__dirname,'../data');
  manager=new Manager({dataDir,catalog});
  window=new BrowserWindow({width:1130,height:790,minWidth:940,minHeight:690,title:'تعريب KH2FM — 1.0.9',backgroundColor:'#f6f7fb',autoHideMenuBar:true,
    webPreferences:{preload:path.join(__dirname,'preload.cjs'),contextIsolation:true,nodeIntegration:false,sandbox:true}});
  window.setMenu(null);
  window.webContents.setWindowOpenHandler(()=>({action:'deny'}));
  window.webContents.on('will-navigate',event=>event.preventDefault());
  window.on('close',event=>{if(busy){event.preventDefault();cancelled=true;closeAfter=true;progress({phase:'cancelling',current:0,total:1});}});
  ipcMain.handle('manager:platform',event=>{trusted(event);return {platform:process.platform,version:app.getVersion()};});
  ipcMain.handle('manager:choose-game',(event)=>respond(async()=>{
    trusted(event); if(busy) throw new Error('انتظر حتى تنتهي العملية الحالية.');
    const result=await dialog.showOpenDialog(window,{title:'اختر مجلد اللعبة',properties:['openDirectory'],defaultPath:selected || undefined});
    if(result.canceled || !result.filePaths.length) return null;
    const choice=result.filePaths[0];
    const inspection=await manager.inspect(choice,prefixOverride);
    selected=choice; return inspection;
  }));
  ipcMain.handle('manager:choose-prefix',event=>respond(async()=>{
    trusted(event); if(busy || !selected) throw new Error('اختر مجلد اللعبة أولًا.');
    const result=await dialog.showOpenDialog(window,{title:'اختر بيئة Wine التي تحتوي user.reg',properties:['openDirectory']});
    if(result.canceled || !result.filePaths.length) return null;
    const inspection=await manager.inspect(selected,result.filePaths[0]);
    if(inspection.needsPrefix) throw new Error('هذا المجلد لا يحتوي بيئة Wine صالحة.');
    prefixOverride=result.filePaths[0]; return inspection;
  }));
  ipcMain.handle('manager:run',(event,operation)=>respond(async()=>{
    trusted(event); if(!['install','remove','undo'].includes(operation)) throw new Error('عملية غير مسموحة.');
    if(busy || !selected) throw new Error('اختر مجلد اللعبة وانتظر انتهاء العملية الحالية.');
    busy=true;cancelled=false;
    try {
      const inspection=await manager.inspect(selected,prefixOverride);
      await ensureGameClosed(inspection.prefix);
      const options={prefixOverride,progress,checkCancel:()=>{if(cancelled) throw new Error('أُلغيت العملية وأُعيدت الملفات إلى حالتها السابقة.');}};
      const context=await manager.context(selected,prefixOverride);
      const result=process.platform==='win32' && await needsElevation(context.gameDir,context.modRoot)
        ? await elevatedOperation(selected,operation,prefixOverride,progress,options.checkCancel)
        : await manager[operation](selected,options);
      return {result,inspection:await manager.inspect(selected,prefixOverride)};
    } finally {busy=false;if(closeAfter) app.quit();}
  }));
  ipcMain.handle('manager:cancel',event=>{trusted(event);cancelled=true;return true;});
  ipcMain.handle('manager:font-report',event=>respond(async()=>{
    trusted(event);if(busy || !selected) throw new Error('اختر مجلد اللعبة وانتظر انتهاء العملية الحالية.');
    const inspection=await manager.inspect(selected,prefixOverride);
    clipboard.writeText(JSON.stringify({managerVersion:app.getVersion(),...inspection},null,2));
    return true;
  }));
  window.loadFile(path.resolve(__dirname,'../ui/index.html'));
});
app.on('window-all-closed',()=>app.quit());
}
