'use strict';
const {app,BrowserWindow,ipcMain,dialog}=require('electron');
const path=require('node:path');
const {execFile}=require('node:child_process');
const {promisify}=require('node:util');
const {Manager}=require('./engine.cjs');
const catalog=require('../catalog/legacy.json');
const exec=promisify(execFile);
let window,manager,selected=null,prefixOverride=null,busy=false,cancelled=false,closeAfter=false;
const respond=async callback=>{try{return {ok:true,value:await callback()};}catch(e){return {ok:false,error:e.message};}};
function trusted(event) { if (!window || event.sender!==window.webContents || event.senderFrame!==window.webContents.mainFrame) throw new Error('طلب غير مسموح.'); }
async function ensureGameClosed() {
  const executable='KINGDOM HEARTS II FINAL MIX.exe';
  if(process.platform==='win32') {
    const {stdout}=await exec('tasklist.exe',['/FI','IMAGENAME eq '+executable,'/FO','CSV','/NH'],{windowsHide:true});
    if(stdout.toLowerCase().includes('"'+executable.toLowerCase()+'"')) throw new Error('أغلق اللعبة قبل التثبيت أو الحذف.');
  } else {
    const {stdout}=await exec('ps',['-ax','-o','comm=']);
    if(stdout.split('\n').some(x=>x.trim().endsWith(executable))) throw new Error('أغلق اللعبة قبل التثبيت أو الحذف.');
    if(process.platform==='darwin' && stdout.split('\n').some(x=>/\/(wine(server|64|32)?|wine-preloader)$/.test(x.trim()))) throw new Error('أغلق اللعبة وSteam داخل Wine أو CrossOver أثناء التثبيت أو الحذف، ثم افتحهما بعد الانتهاء.');
  }
}
function progress(message) { if(window && !window.isDestroyed()) window.webContents.send('manager:progress',message); }
app.setName('KH2FM Arabic');
app.whenReady().then(()=>{
  const dataDir=app.isPackaged ? path.join(process.resourcesPath,'translation') : path.resolve(__dirname,'../data');
  manager=new Manager({dataDir,catalog});
  window=new BrowserWindow({width:1130,height:790,minWidth:940,minHeight:690,title:'تعريب KH2FM — 1.0.3',backgroundColor:'#f6f7fb',autoHideMenuBar:true,
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
      await ensureGameClosed();
      const options={prefixOverride,progress,checkCancel:()=>{if(cancelled) throw new Error('أُلغيت العملية وأُعيدت الملفات إلى حالتها السابقة.');}};
      const result=await manager[operation](selected,options);
      return {result,inspection:await manager.inspect(selected,prefixOverride)};
    } finally {busy=false;if(closeAfter) app.quit();}
  }));
  ipcMain.handle('manager:cancel',event=>{trusted(event);cancelled=true;return true;});
  window.loadFile(path.resolve(__dirname,'../ui/index.html'));
});
app.on('window-all-closed',()=>app.quit());
