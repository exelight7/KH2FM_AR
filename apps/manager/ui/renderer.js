'use strict';
const $=id=>document.getElementById(id);
let inspection=null,busy=false,platform='win32';
let updateState={status:'idle'},managerVersion='1.0.13';
const updateBusy=()=>['checking','downloading','cancelling','restarting'].includes(updateState.status);
const api=window.kh2fm;
let initializing=typeof api.bootstrap==='function';
if(initializing)$('choose-game').disabled=true;
function showFeedback(title,text,error=false){$('feedback-title').textContent=title;$('feedback-text').textContent=text;$('feedback').classList.toggle('error',error);$('feedback').hidden=false;$('feedback').scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
function closeMenu(){$('management-menu').hidden=true;$('menu-toggle').setAttribute('aria-expanded','false');}
function refresh(value){
  inspection=value;
  const locked=busy || updateBusy() || initializing;
  if(value){$('game-path').textContent=value.gameDir;$('game-path').hidden=false;$('folder-label').textContent='تغيير مجلد اللعبة';}
  $('install').disabled=locked || !value || value.pendingRecovery || value.needsPrefix;
  $('choose-game').disabled=locked;
  $('remove').disabled=locked || !value?.installed || value.pendingRecovery;
  $('undo').disabled=locked || (!value?.canUndo && !value?.pendingRecovery);
  $('prefix').disabled=locked || !value;
  $('font-report').disabled=locked || !value;
  $('launcher-update').disabled=busy || initializing;
  $('undo').lastChild.textContent=value?.pendingRecovery ? 'استعادة العملية السابقة' : 'التراجع عن آخر عملية';
  $('install-label').textContent=busy ? 'جاري العمل…' : value?.installed ? (value.version===managerVersion ? 'إعادة تثبيت التعريب' : 'تحديث التعريب إلى '+managerVersion) : 'تثبيت التعريب';
  $('selection-status').classList.toggle('ready',!!value && !value.needsPrefix && !value.pendingRecovery && !value.fontCheck?.issues.length);
  $('selection-text').textContent=!value ? 'أنت تختار المجلد، ونحن نكمل الباقي.' : value.pendingRecovery ? 'عملية سابقة لم تكتمل — الاستعادة متاحة في القائمة.' : value.needsPrefix ? 'شغّل اللعبة مرة واحدة، أو اختر بيئة Wine من القائمة.' : value.installed ? 'التعريب '+value.version+' موجود — يمكنك تحديثه أو حذفه.' : 'مجلد اللعبة جاهز للتثبيت.';
  if(value?.fontCheck?.issues.length && !value.pendingRecovery && !value.needsPrefix) $('selection-text').textContent=value.fontCheck.issues.join(' ');
}
async function choose(which){
  closeMenu();
  const result=await api[which]();
  if(!result.ok){showFeedback('راجع المجلد المختار',result.error,true);return;}
  if(result.value){$('feedback').hidden=true;refresh(result.value);}
}
async function run(operation){
  closeMenu();if(busy || updateBusy() || initializing)return;
  busy=true;$('feedback').hidden=true;$('progress-area').hidden=false;$('progress-fill').style.width='0%';$('progress-percent').textContent='0%';$('progress-label').textContent=operation==='undo' ? 'استعادة الحالة السابقة' : 'تجهيز العملية';$('cancel').hidden=operation==='undo';$('cancel').disabled=false;$('cancel').textContent='إلغاء العملية';refresh(inspection);$('progress-area').scrollIntoView({block:'nearest',behavior:'instant'});
  try{
    const response=await api.run(operation);
    if(!response.ok){showFeedback('لم تكتمل العملية',response.error,true);return;}
    refresh(response.value.inspection);
    if(operation==='install' && response.value.inspection.fontCheck?.issues.length)showFeedback('تحتاج إعدادات الخط إلى مراجعة',response.value.inspection.fontCheck.issues.join(' ')+' انسخ تقرير فحص الخط من القائمة.',true);
    else if(operation==='install')showFeedback('التعريب جاهز ✦','تم التحقق من ملفات الخط ومسار المودات. اختر English كلغة اللعبة في Steam، ثم شغّل اللعبة.');
    else if(operation==='remove')showFeedback('تم حذف التعريب','يمكنك التراجع عن الحذف من القائمة إذا أردت إعادته.');
    else showFeedback('تمت الاستعادة','رجعت الملفات إلى حالتها قبل العملية الأخيرة.');
  }catch(error){showFeedback('تعذر إكمال العملية',error.message,true);}
  finally{busy=false;$('progress-area').hidden=true;refresh(inspection);renderUpdate(updateState);}
}
function renderUpdate(value){
  updateState=value;
  const version=value.version || '',percent=Math.round(value.percent || 0);
  const text={idle:'تحقق من آخر إصدار متاح.',checking:'جاري التحقق من التحديثات…',current:'أنت تستخدم أحدث إصدار: '+managerVersion,available:'يتوفر الإصدار '+version+' للانشر والتعريب.',downloading:'جاري تنزيل الإصدار '+version+' — '+percent+'%',cancelling:'جاري إلغاء التنزيل…',downloaded:'اكتمل التنزيل والتحقق من التحديث. أغلق اللعبة قبل إعادة التشغيل لتطبيق التعريب.',restarting:'جاري تثبيت التحديث وإعادة تشغيل اللانشر…',error:'تعذر إكمال التحديث. تحقق من الاتصال والمساحة المتاحة، ثم أعد المحاولة.',unsupported:'التحديث الداخلي متاح في مثبت Windows ونسخة Linux AppImage.'};
  $('update-status').textContent=text[value.status] || text.error;
  $('update-action').textContent=value.status==='available' ? 'تنزيل الإصدار '+version : value.status==='downloaded' ? 'التحديث وإعادة التشغيل' : value.status==='error' ? 'إعادة المحاولة' : 'التحقق من التحديثات';
  $('update-action').disabled=busy || updateBusy() || value.status==='unsupported';
  $('update-progress').hidden=!['downloading','cancelling'].includes(value.status);
  $('update-progress').setAttribute('aria-valuenow',String(percent));$('update-progress-fill').style.width=percent+'%';
  $('update-cancel').hidden=!['downloading','cancelling'].includes(value.status);$('update-cancel').disabled=value.status==='cancelling';
  $('launcher-update').textContent=value.status==='downloading' ? 'تنزيل التحديث '+percent+'%' : value.status==='downloaded' ? 'التحديث جاهز' : 'تحديث اللانشر';
  refresh(inspection);
}
async function requestUpdate(){
  if(busy || updateBusy())return;
  const operation=updateState.status==='available'?'download':updateState.status==='downloaded'?'restart':'check';
  try{const result=await api.update(operation);if(result.ok)renderUpdate(result.value);else $('update-status').textContent=result.error;}catch(error){$('update-status').textContent=error.message;}
}
$('launcher-update').addEventListener('click',()=>{closeMenu();$('update-dialog').showModal();if(['idle','current','error'].includes(updateState.status))requestUpdate();});
$('close-update').addEventListener('click',()=>$('update-dialog').close());
$('update-action').addEventListener('click',requestUpdate);
$('update-cancel').addEventListener('click',()=>api.cancelUpdate());
api.onUpdate?.(renderUpdate);
$('choose-game').addEventListener('click',()=>choose('chooseGame'));
$('prefix').addEventListener('click',()=>choose('choosePrefix'));
$('install').addEventListener('click',()=>run('install'));
$('remove').addEventListener('click',()=>run('remove'));
$('undo').addEventListener('click',()=>run('undo'));
$('font-report').addEventListener('click',async()=>{closeMenu();try{const result=await api.fontReport();showFeedback(result.ok?'نُسخ تقرير الخط':'تعذر نسخ التقرير',result.ok?'الصق التقرير في المحادثة لفحص مسارات الخط وملفاته.':result.error,!result.ok);}catch(error){showFeedback('تعذر نسخ التقرير',error.message,true);}});
$('cancel').addEventListener('click',async()=>{$('cancel').disabled=true;$('cancel').textContent='جاري الإلغاء والاستعادة…';await api.cancel();});
$('menu-toggle').addEventListener('click',()=>{$('management-menu').hidden=!$('management-menu').hidden;$('menu-toggle').setAttribute('aria-expanded',String(!$('management-menu').hidden));});
document.addEventListener('click',event=>{if(!event.target.closest('.menu-wrap'))closeMenu();});
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeMenu();});
$('help').addEventListener('click',()=>{closeMenu();$('help-dialog').showModal();});
$('close-help').addEventListener('click',()=>$('help-dialog').close());
api.onProgress(message=>{
  const labels={verify:'التحقق من حزمة التعريب',extract:'تجهيز ملفات التعريب',backup:'حفظ الحالة السابقة',apply:'كتابة الملفات والتحقق منها',cancelling:'إلغاء العملية واستعادة الملفات'};
  const fractions={verify:[0,10],extract:[10,55],backup:[55,60],apply:[60,100]};
  const bounds=fractions[message.phase] || [0,0];
  const percent=Math.round(bounds[0]+(bounds[1]-bounds[0])*message.current/Math.max(1,message.total));
  $('progress-label').textContent=labels[message.phase] || 'جاري العمل';$('progress-percent').textContent=percent+'%';$('progress-fill').style.width=percent+'%';document.querySelector('[role="progressbar"]').setAttribute('aria-valuenow',String(percent));
});
api.platform().then(value=>{platform=value.platform;
  managerVersion=value.version || managerVersion;
  $('platform-badge').textContent=platform==='win32' ? 'WINDOWS' : platform==='darwin' ? 'macOS · WINE / CROSSOVER' : 'LINUX · STEAM / PROTON';
  $('prefix').hidden=platform==='win32';
  $('platform-hint').textContent=platform==='darwin' ? 'اختر مجلد نسخة اللعبة داخل Wine أو CrossOver.' : platform==='linux' ? 'اختر مجلد نسخة Steam التي تشغّلها عبر Proton.' : 'اختر مجلد KINGDOM HEARTS -HD 1.5+2.5 ReMIX-.';
  refresh(null);
  if(api.bootstrap)api.bootstrap().then(result=>{
    initializing=false;
    if(!result.ok || !result.value){refresh(inspection);return;}
    refresh(result.value.inspection);renderUpdate(result.value.update);
    if(result.value.applyPending && inspection && !inspection.needsPrefix && !inspection.pendingRecovery)run('install');
  }).catch(error=>{initializing=false;refresh(inspection);showFeedback('تعذر استعادة المجلد المحفوظ',error.message,true);});
});
