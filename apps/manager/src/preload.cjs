'use strict';
const {contextBridge,ipcRenderer}=require('electron');
contextBridge.exposeInMainWorld('kh2fm',{
  platform:()=>ipcRenderer.invoke('manager:platform'),
  bootstrap:()=>ipcRenderer.invoke('manager:bootstrap'),
  update:operation=>ipcRenderer.invoke('manager:update',operation),
  cancelUpdate:()=>ipcRenderer.invoke('manager:update-cancel'),
  chooseGame:()=>ipcRenderer.invoke('manager:choose-game'),
  choosePrefix:()=>ipcRenderer.invoke('manager:choose-prefix'),
  run:operation=>ipcRenderer.invoke('manager:run',operation),
  cancel:()=>ipcRenderer.invoke('manager:cancel'),
  fontReport:()=>ipcRenderer.invoke('manager:font-report'),
  onUpdate:callback=>{const listener=(_event,value)=>callback(value);ipcRenderer.on('manager:update-state',listener);return ()=>ipcRenderer.removeListener('manager:update-state',listener);},
  onProgress:callback=>{const listener=(_event,message)=>callback(message);ipcRenderer.on('manager:progress',listener);return ()=>ipcRenderer.removeListener('manager:progress',listener);}
});
