'use strict';
const {app}=require('electron');
const {fs,path,crypto,exists,assertRegular,hashBytes,readJSON,writeJSON}=require('./paths.cjs');
const {Manager}=require('./engine.cjs');
const catalog=require('../catalog/legacy.json');
const {execFile}=require('node:child_process');
const {promisify}=require('node:util');
const exec=promisify(execFile);

async function needsElevation(game,mod) {
  for(const directory of [...new Set([game,mod])]) {
    if(!(await exists(directory)))continue;
    await assertRegular(directory);
    const probe=path.join(directory,'.kh2fm-permission-'+crypto.randomUUID());
    try {const handle=await fs.open(probe,'wx');await handle.close();await fs.rm(probe);}
    catch(error){if(['EACCES','EPERM'].includes(error.code))return true;throw error;}
  }
  return false;
}
async function elevatedOperation(game,operation,prefixOverride,progress,checkCancel) {
  const directory=path.join(app.getPath('userData'),'jobs','job-'+crypto.randomUUID());
  await assertRegular(directory);await fs.mkdir(directory,{recursive:true});
  const request=path.join(directory,'request.json');
  await writeJSON(request,{schema:1,game,operation,prefixOverride});
  const digest=hashBytes(await fs.readFile(request));
  const quote=value=>"'"+value.replaceAll("'","''")+"'";
  const executable=process.execPath;
  const argumentsString='"--manager-job='+request+'" "--manager-job-hash='+digest+'"';
  const command='$ErrorActionPreference='+quote('Stop')+'; $jobProcess=Start-Process -FilePath '+quote(executable)+' -ArgumentList '+quote(argumentsString)+' -Verb RunAs -PassThru; $jobProcess.WaitForExit(); exit $jobProcess.ExitCode';
  const encoded=Buffer.from(command,'utf16le').toString('base64');
  let cancelSent=false,previousProgress='';
  const timer=setInterval(async()=>{
    try {
      try{checkCancel();}catch{if(!cancelSent){cancelSent=true;await writeJSON(path.join(directory,'cancel.json'),{cancel:true});}}
      const progressFile=path.join(directory,'progress.json');
      if(await exists(progressFile)){const value=await fs.readFile(progressFile,'utf8');if(value!==previousProgress){previousProgress=value;progress(JSON.parse(value));}}
    }catch{ /* A progress file can be replaced while this reader polls. */ }
  },250);
  try {
    await exec('powershell.exe',['-NoProfile','-NonInteractive','-EncodedCommand',encoded],{windowsHide:true,timeout:15*60*1000,maxBuffer:1024*1024});
    const result=await readJSON(path.join(directory,'result.json'));
    if(!result.ok)throw new Error(result.error);
    return result.value;
  }catch(error){
    if(await exists(path.join(directory,'result.json'))){const result=await readJSON(path.join(directory,'result.json'));throw new Error(result.error || error.message);}
    throw new Error('لم تكتمل موافقة صلاحية المسؤول. أغلق أي نسخة أخرى من البرنامج وأعد المحاولة.');
  }finally{clearInterval(timer);}
}
async function runWorker(request,digest) {
  await assertRegular(request);
  if(!/^job-[0-9a-f-]{36}$/.test(path.basename(path.dirname(request))) || path.basename(request)!=='request.json' || !/^[a-f0-9]{64}$/.test(digest))throw new Error('طلب صلاحية غير صالح.');
  const bytes=await fs.readFile(request);
  if(hashBytes(bytes)!==digest)throw new Error('تغير طلب التثبيت؛ أوقفنا العملية.');
  const job=JSON.parse(bytes),directory=path.dirname(request);
  if(job.schema!==1 || !['install','remove','undo'].includes(job.operation) || typeof job.game!=='string')throw new Error('طلب التثبيت غير صالح.');
  const dataDir=app.isPackaged?path.join(process.resourcesPath,'translation'):path.resolve(__dirname,'../data');
  const manager=new Manager({dataDir,catalog});
  let lastProgress=0;
  try {
    const value=await manager[job.operation](job.game,{prefixOverride:job.prefixOverride,
      checkCancel:()=>{if(require('node:fs').existsSync(path.join(directory,'cancel.json')))throw new Error('أُلغيت العملية وأُعيدت الملفات إلى حالتها السابقة.');},
      progress:message=>{const now=Date.now();if(now-lastProgress>200){lastProgress=now;require('node:fs').writeFileSync(path.join(directory,'progress.json'),JSON.stringify(message));}}
    });
    await writeJSON(path.join(directory,'result.json'),{ok:true,value});
    return 0;
  }catch(error){await writeJSON(path.join(directory,'result.json'),{ok:false,error:error.message});return 1;}
}
module.exports={needsElevation,elevatedOperation,runWorker};
