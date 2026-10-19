'use strict';
const {CancellationToken}=require('builder-util-runtime');

// electron-updater verifies the release's SHA-512 before reporting downloaded.
// The feed is fixed in the packaged app-update.yml; renderer input cannot set it.
class Updates {
  constructor({updater,version,supported=true,changed=()=>{},isBusy=()=>false,beforeRestart=async()=>{},schedule=callback=>setTimeout(callback,250)}) {
    Object.assign(this,{updater,changed,isBusy,beforeRestart,schedule});
    this.state={status:supported?'idle':'unsupported',currentVersion:version,version:null,percent:0};
    updater.autoDownload=false;
    updater.autoInstallOnAppQuit=false;
    updater.allowPrerelease=false;
    updater.disableDifferentialDownload=true;
    updater.on('update-available',info=>this.set({status:'available',version:info.version,percent:0}));
    updater.on('update-not-available',()=>this.set({status:'current',version:null,percent:0}));
    updater.on('download-progress',info=>{if(this.state.status==='downloading')this.set({percent:Math.max(0,Math.min(100,Number(info.percent)||0))});});
    updater.on('update-downloaded',info=>this.set({status:'downloaded',version:info.version,percent:100}));
    updater.on('error',()=>{if(this.state.status!=='cancelling')this.set({status:'error',percent:0});});
  }
  get busy() {return ['checking','downloading','cancelling','restarting'].includes(this.state.status);}
  set(value) {Object.assign(this.state,value);this.changed({...this.state});}
  guard() {
    if(this.state.status==='unsupported')throw new Error('التحديث الداخلي متاح في مثبت Windows ونسخة Linux AppImage.');
    if(this.isBusy() || this.busy)throw new Error('انتظر انتهاء العملية الحالية أولًا.');
  }
  async check() {
    this.guard();this.set({status:'checking',version:null,percent:0});
    try {
      const result=await this.updater.checkForUpdates();
      this.token=result?.cancellationToken;
      if(this.state.status==='checking')this.set({status:'current'});
    }catch{this.set({status:'error'});}
    return {...this.state};
  }
  async download() {
    this.guard();
    if(this.state.status!=='available')throw new Error('تحقق من وجود تحديث جديد أولًا.');
    this.token=new CancellationToken();
    this.set({status:'downloading',percent:0});
    try {
      await this.updater.downloadUpdate(this.token);
      if(this.state.status==='downloading')this.set({status:'error',percent:0});
    }catch{this.set({status:this.state.status==='cancelling'?'available':'error',percent:0});}
    return {...this.state};
  }
  cancel() {
    if(this.state.status!=='downloading')return;
    this.set({status:'cancelling'});this.token?.cancel();
  }
  async restart() {
    this.guard();
    if(this.state.status!=='downloaded')throw new Error('انتظر تنزيل التحديث والتحقق منه أولًا.');
    this.set({status:'restarting'});
    try{await this.beforeRestart(this.state.version);}catch(error){this.set({status:'downloaded'});throw error;}
    this.schedule(()=>{try{this.updater.quitAndInstall(true,true);}catch{this.set({status:'error'});}});
    return {...this.state};
  }
}
module.exports={Updates};
