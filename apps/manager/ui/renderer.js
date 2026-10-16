'use strict';
const $=id=>document.getElementById(id);
let inspection=null,busy=false,platform='win32';
const api=window.kh2fm;
function showFeedback(title,text,error=false){$('feedback-title').textContent=title;$('feedback-text').textContent=text;$('feedback').classList.toggle('error',error);$('feedback').hidden=false;$('feedback').scrollIntoView({block:'nearest',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
function closeMenu(){$('management-menu').hidden=true;$('menu-toggle').setAttribute('aria-expanded','false');}
function refresh(value){
  inspection=value;
  if(value){$('game-path').textContent=value.gameDir;$('game-path').hidden=false;$('folder-label').textContent='تغيير مجلد اللعبة';}
  $('install').disabled=busy || !value || value.pendingRecovery || value.needsPrefix;
  $('choose-game').disabled=busy;
  $('remove').disabled=busy || !value?.installed || value.pendingRecovery;
  $('undo').disabled=busy || (!value?.canUndo && !value?.pendingRecovery);
  $('prefix').disabled=busy || !value;
  $('undo').lastChild.textContent=value?.pendingRecovery ? 'استعادة العملية السابقة' : 'التراجع عن آخر عملية';
  $('install-label').textContent=busy ? 'جاري العمل…' : value?.installed ? (value.version==='1.0.5' ? 'إعادة تثبيت التعريب' : 'تحديث التعريب إلى 1.0.5') : 'تثبيت التعريب';
  $('selection-status').classList.toggle('ready',!!value && !value.needsPrefix && !value.pendingRecovery);
  $('selection-text').textContent=!value ? 'أنت تختار المجلد، ونحن نكمل الباقي.' : value.pendingRecovery ? 'عملية سابقة لم تكتمل — الاستعادة متاحة في القائمة.' : value.needsPrefix ? 'شغّل اللعبة مرة واحدة، أو اختر بيئة Wine من القائمة.' : value.installed ? 'التعريب '+value.version+' موجود — يمكنك تحديثه أو حذفه.' : 'مجلد اللعبة جاهز للتثبيت.';
}
async function choose(which){
  closeMenu();
  const result=await api[which]();
  if(!result.ok){showFeedback('راجع المجلد المختار',result.error,true);return;}
  if(result.value){$('feedback').hidden=true;refresh(result.value);}
}
async function run(operation){
  closeMenu();if(busy)return;
  busy=true;$('feedback').hidden=true;$('progress-area').hidden=false;$('progress-fill').style.width='0%';$('progress-percent').textContent='0%';$('progress-label').textContent=operation==='undo' ? 'استعادة الحالة السابقة' : 'تجهيز العملية';$('cancel').hidden=operation==='undo';$('cancel').disabled=false;$('cancel').textContent='إلغاء العملية';refresh(inspection);$('progress-area').scrollIntoView({block:'nearest',behavior:'instant'});
  try{
    const response=await api.run(operation);
    if(!response.ok){showFeedback('لم تكتمل العملية',response.error,true);return;}
    refresh(response.value.inspection);
    if(operation==='install')showFeedback('التعريب جاهز ✦','اختر English كلغة اللعبة في Steam، ثم شغّل اللعبة واستمتع.');
    else if(operation==='remove')showFeedback('تم حذف التعريب','يمكنك التراجع عن الحذف من القائمة إذا أردت إعادته.');
    else showFeedback('تمت الاستعادة','رجعت الملفات إلى حالتها قبل العملية الأخيرة.');
  }catch(error){showFeedback('تعذر إكمال العملية',error.message,true);}
  finally{busy=false;$('progress-area').hidden=true;refresh(inspection);}
}
$('choose-game').addEventListener('click',()=>choose('chooseGame'));
$('prefix').addEventListener('click',()=>choose('choosePrefix'));
$('install').addEventListener('click',()=>run('install'));
$('remove').addEventListener('click',()=>run('remove'));
$('undo').addEventListener('click',()=>run('undo'));
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
  $('platform-badge').textContent=platform==='win32' ? 'WINDOWS' : platform==='darwin' ? 'macOS · WINE / CROSSOVER' : 'LINUX · STEAM / PROTON';
  $('prefix').hidden=platform==='win32';
  $('platform-hint').textContent=platform==='darwin' ? 'اختر مجلد نسخة اللعبة داخل Wine أو CrossOver.' : platform==='linux' ? 'اختر مجلد نسخة Steam التي تشغّلها عبر Proton.' : 'اختر مجلد KINGDOM HEARTS -HD 1.5+2.5 ReMIX-.';
  refresh(null);
});
