'use strict';
const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('kh2fm',{
  platform:()=>ipcRenderer.invoke('manager:platform'),
  chooseGame:()=>ipcRenderer.invoke('manager:choose-game'),
  choosePrefix:()=>ipcRenderer.invoke('manager:choose-prefix'),
  run:operation=>ipcRenderer.invoke('manager:run',operation),
  cancel:()=>ipcRenderer.invoke('manager:cancel'),
  fontReport:()=>ipcRenderer.invoke('manager:font-report'),
  onProgress:callback=>{const listener=(_event,message)=>callback(message);ipcRenderer.on('manager:progress',listener);return ()=>ipcRenderer.removeListener('manager:progress',listener);}
});
