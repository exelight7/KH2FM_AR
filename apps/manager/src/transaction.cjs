'use strict';
const {fs, path, crypto, exists, assertRegular, hash, hashBytes, readJSON, atomicWrite, atomicCopy, writeJSON} = require('./paths.cjs');

async function snapshotOperation(meta, context, actions, kind) {
  const id = crypto.randomUUID();
  const directory = path.join(meta, 'operations', id);
  await assertRegular(directory); await fs.mkdir(path.join(directory,'backup'),{recursive:true});
  const journal = {schema:1, id, kind, createdAt:new Date().toISOString(), phase:'preparing', context, records:[]};
  const journalPath = path.join(directory,'journal.json');
  await writeJSON(journalPath,journal);
  for (let i=0;i<actions.length;i++) {
    const action=actions[i]; await assertRegular(action.target);
    const before=await hash(action.target);
    if (before!==action.beforeHash) throw new Error('تغيّر ملف أثناء الفحص. أعد المحاولة بعد إغلاق اللعبة.');
    const backup=before ? 'backup/'+i+'.bin' : null;
    if (backup) {
      await fs.copyFile(action.target,path.join(directory,backup));
      if (await hash(path.join(directory,backup))!==before) throw new Error('تعذر التحقق من النسخة الاحتياطية.');
    }
    const after=action.data!==undefined ? hashBytes(action.data) : action.source ? await hash(action.source) : null;
    journal.records.push({target:action.target,beforeHash:before,afterHash:after,backup,mayApply:false});
  }
  journal.phase='prepared'; await writeJSON(journalPath,journal);
  return {directory,journal,journalPath,actions};
}
async function restoreOperation(operation, allowedTarget) {
  const {directory,journal,journalPath}=operation;
  if (journal.schema!==1 || !Array.isArray(journal.records) || journal.records.length>1000) throw new Error('سجل الاستعادة غير صالح.');
  const records=journal.records.filter(x=>x.mayApply);
  for (const record of records) {
    if (!allowedTarget(record.target,journal.context)) throw new Error('سجل الاستعادة يحتوي مسارًا غير مسموح.');
    await assertRegular(record.target);
    const current=await hash(record.target);
    if (current!==record.beforeHash && current!==record.afterHash) throw new Error('تغيّر ملف بعد العملية؛ أوقفنا الاستعادة لحماية تغييراتك.');
    if (record.beforeHash) {
      if (!/^backup\/\d+\.bin$/.test(record.backup || '')) throw new Error('مسار النسخة الاحتياطية غير صالح.');
      if (await hash(path.join(directory,record.backup))!==record.beforeHash) throw new Error('النسخة الاحتياطية تغيرت أو لم تعد موجودة.');
    }
  }
  journal.phase='restoring'; await writeJSON(journalPath,journal);
  for (const record of [...records].reverse()) {
    if (await hash(record.target)===record.beforeHash) continue;
    if (record.backup) await atomicCopy(path.join(directory,record.backup),record.target);
    else await fs.rm(record.target,{force:true});
  }
  journal.phase='restored'; await writeJSON(journalPath,journal);
}
async function applyOperation(operation, options) {
  const {journal,journalPath,actions}=operation;
  journal.phase='applying'; await writeJSON(journalPath,journal);
  try {
    for (let i=0;i<actions.length;i++) {
      options.checkCancel?.();
      const action=actions[i], record=journal.records[i];
      if (await hash(action.target)!==record.beforeHash) throw new Error('تغيّر ملف أثناء التثبيت.');
      record.mayApply=true; await writeJSON(journalPath,journal);
      if (action.data!==undefined) await atomicWrite(action.target,action.data);
      else if (action.source) await atomicCopy(action.source,action.target);
      else await fs.rm(action.target,{force:true});
      if (await hash(action.target)!==record.afterHash) throw new Error('فشل التحقق من ملف بعد النسخ.');
      await options.afterWrite?.(i,action);
      options.progress?.({phase:'apply',current:i+1,total:actions.length});
    }
    journal.phase='committed'; await writeJSON(journalPath,journal);
    return journal.id;
  } catch (error) {
    try { await restoreOperation(operation,options.allowedTarget); }
    catch (restoreError) { throw new Error(error.message+' تعذر إكمال الاستعادة: '+restoreError.message+' النسخة الاحتياطية محفوظة؛ استخدم استعادة العملية من القائمة.'); }
    throw error;
  }
}
async function loadOperation(directory) { return {directory,journal:await readJSON(path.join(directory,'journal.json')),journalPath:path.join(directory,'journal.json')}; }
async function operations(meta) {
  const root=path.join(meta,'operations');
  if (!(await exists(root))) return [];
  await assertRegular(root);
  const result=[];
  for (const item of await fs.readdir(root,{withFileTypes:true})) {
    if (!item.isDirectory() || !/^[0-9a-f-]{36}$/.test(item.name)) continue;
    const directory=path.join(root,item.name);
    if (await exists(path.join(directory,'journal.json'))) result.push(await loadOperation(directory));
  }
  return result.sort((a,b)=>b.journal.createdAt.localeCompare(a.journal.createdAt));
}
module.exports={snapshotOperation,applyOperation,restoreOperation,operations,loadOperation};
