'use strict';
const os = require('node:os');
const zlib = require('node:zlib');
const {pipeline} = require('node:stream/promises');
const {fs,fss,path,crypto,exists,assertRegular,safeJoin,hash,hashBytes,readJSON,atomicCopy,writeJSON,filesBelow} = require('./paths.cjs');
const {GAME_EXE,REG_SECTION,REG_LINE,discoverPrefix,settingsRoot,settingsValue,windowsPathToHost,registryValue,patchRegistry} = require('./compatibility.cjs');
const {snapshotOperation,applyOperation,restoreOperation,operations} = require('./transaction.cjs');
const META = '.kh2fm-arabic';
const SHA = /^[a-f0-9]{64}$/;
const samePath=(a,b)=>process.platform==='win32' ? path.resolve(a).toLowerCase()===path.resolve(b).toLowerCase() : path.resolve(a)===path.resolve(b);

class Manager {
  constructor({dataDir,catalog,platform=process.platform,legacyAppDirs=[]}) {
    this.dataDir=dataDir; this.catalog=catalog; this.platform=platform; this.legacyAppDirs=legacyAppDirs;
  }
  async manifest() {
    const manifest=await readJSON(path.join(this.dataDir,'manifest.json'));
    if (manifest.schema!==1 || manifest.version!=='1.0.5' || !Array.isArray(manifest.files) || manifest.files.length>900 || !SHA.test(manifest.blobHash)) throw new Error('حزمة التعريب غير صالحة. أعد تنزيل البرنامج.');
    const seen=new Set();
    for (const entry of manifest.files) {
      if (!['payload','loader'].includes(entry.group) || !SHA.test(entry.sha256) || !Number.isSafeInteger(entry.size) || entry.size<0 || !Number.isSafeInteger(entry.offset) || entry.offset<0 || !Number.isSafeInteger(entry.compressedSize) || entry.compressedSize<=0) throw new Error('سجل الحزمة غير صالح.');
      safeJoin(this.dataDir,entry.path);
      if (entry.group==='payload' && (!/^kh2\/.+\.(bar|png|dds)$/i.test(entry.path) || !this.catalog.versions.some(v=>v.files.some(x=>x.path===entry.path)))) throw new Error('الحزمة تحتوي ملفًا غير مسموح.');
      if (entry.group==='loader' && !this.catalog.loader.some(x=>x.path===entry.path && x.sha256===entry.sha256)) throw new Error('ملف محمل المودات لا يطابق المصدر المعتمد.');
      if (seen.has(entry.path)) throw new Error('الحزمة تحتوي مسارات مكررة.');
      seen.add(entry.path);
    }
    return manifest;
  }
  knownArabic(relative,digest) { return this.catalog.versions.some(v=>v.files.some(f=>f.path==='kh2/'+relative && f.sha256===digest)); }
  async validateGame(gameDir) {
    if (typeof gameDir!=='string' || !gameDir.trim()) throw new Error('اختر مجلد اللعبة أولًا.');
    gameDir=path.resolve(gameDir);
    if(!(await exists(gameDir))) throw new Error('مجلد اللعبة غير موجود.');
    gameDir=await fs.realpath(gameDir);
    await assertRegular(gameDir);
    const exe=path.join(gameDir,GAME_EXE);
    if (!(await exists(exe)) || !(await fs.stat(exe)).isFile()) throw new Error('هذا المجلد لا يحتوي KINGDOM HEARTS II FINAL MIX.exe. اختر مجلد اللعبة الصحيح.');
    await assertRegular(exe);
    return gameDir;
  }
  async context(gameDir,prefixOverride) {
    const chosenDir=path.resolve(gameDir);
    gameDir=await this.validateGame(gameDir);
    const manifest=await this.manifest();
    const meta=path.join(gameDir,META); await assertRegular(meta);
    const prefix=await discoverPrefix(chosenDir,this.platform,prefixOverride);
    let state=null;
    if (await exists(path.join(meta,'state.json'))) {
      state=await readJSON(path.join(meta,'state.json'));
      await this.validateState(state,gameDir,manifest);
      if(state.registry && (this.platform==='win32' || !prefix || !samePath(state.registry.prefix,prefix))) throw new Error('بيئة Wine لا تطابق سجل التعريب.');
    }
    const modRoot=state ? path.resolve(state.modRoot) : await settingsRoot(gameDir,prefix,this.platform);
    await assertRegular(modRoot);
    if (samePath(modRoot,gameDir) || samePath(modRoot,path.parse(gameDir).root)) throw new Error('مسار المودات غير صالح.');
    return {gameDir,meta,prefix,manifest,state,modRoot};
  }
  async validateState(state,gameDir,manifest) {
    if (state.schema!==2 || !['1.0.3','1.0.4','1.0.5'].includes(state.version) || !samePath(state.gameDir,gameDir) || typeof state.modRoot!=='string' || !path.isAbsolute(state.modRoot) || !Array.isArray(state.entries) || state.entries.length>900) throw new Error('سجل التعريب غير صالح أو يعود إلى لعبة أخرى.');
    // 1.0.3 shipped exactly the 1.0.2 translation; validate its records against
    // those pinned bytes so updating the font does not invalidate upgrades/undo.
    const previousVersion=state.version==='1.0.3' ? '1.0.2' : state.version;
    const statePayload=state.version==='1.0.5'
      ? manifest.files.filter(x=>x.group==='payload')
      : (this.catalog.versions.find(v=>v.version===previousVersion)?.files || []);
    const seen=new Set();
    for (const entry of state.entries) {
      const key=entry.root+':'+entry.path;
      if (seen.has(key) || !['mod','game'].includes(entry.root) || !SHA.test(entry.sha256)) throw new Error('سجل التعريب غير صالح.');
      seen.add(key);
      const permitted=entry.root==='mod' ? statePayload.some(x=>x.path===entry.path && x.sha256===entry.sha256) : this.catalog.loader.some(x=>x.path===entry.path && x.sha256===entry.sha256) || entry.path==='panacea_settings.txt';
      if (!permitted) throw new Error('سجل التعريب يحتوي ملفًا غير مسموح.');
      safeJoin(entry.root==='mod' ? state.modRoot : gameDir,entry.path);
      if (entry.original && (!/^originals\/[a-f0-9]{32}\.bin$/.test(entry.original.path) || !SHA.test(entry.original.sha256))) throw new Error('سجل النسخة الأصلية غير صالح.');
    }
    if (state.registry && (state.registry.section!==REG_SECTION || !['version','dbghelp'].includes(state.registry.name) || state.registry.afterLine!=='"'+state.registry.name+'"="native,builtin"' || typeof state.registry.prefix!=='string')) throw new Error('سجل إعدادات Wine غير صالح.');
  }
  allowedTarget(target,context) {
    if (!samePath(context.gameDir,this.activeGame || context.gameDir)) return false;
    const game=path.resolve(context.gameDir), mod=path.resolve(context.modRoot), meta=path.join(game,META);
    if (samePath(target,path.join(meta,'state.json'))) return true;
    if (context.prefix && samePath(target,path.join(context.prefix,'user.reg'))) return true;
    if (samePath(target,path.join(game,'panacea_settings.txt'))) return true;
    if (this.catalog.loader.some(x=>samePath(target,safeJoin(game,x.path)))) return true;
    return this.catalog.versions.some(v=>v.files.some(x=>samePath(target,safeJoin(mod,x.path))));
  }
  async inspect(gameDir,prefixOverride) {
    const c=await this.context(gameDir,prefixOverride);
    const history=await operations(c.meta);
    const pending=history.find(x=>['applying','restoring'].includes(x.journal.phase));
    const last=history[0];
    let legacyVersion=null;
    if (!c.state) {
      for (const version of this.catalog.versions) {
        const anchors=version.files.filter(x=>/^kh2\/msg\/us\/(sys|tt|eh)\.bar$/.test(x.path));
        if (anchors.length && (await Promise.all(anchors.map(async x=>await hash(safeJoin(c.modRoot,x.path))===x.sha256))).every(Boolean)) { legacyVersion=version.version; break; }
      }
    }
    const installed=!!c.state || !!legacyVersion;
    return {gameDir:c.gameDir,installed,version:c.state?.version || legacyVersion,platform:this.platform,
      prefix:c.prefix,needsPrefix:this.platform!=='win32' && !c.prefix,pendingRecovery:!!pending,
      canUndo:!!last && last.journal.phase==='committed',lastOperation:last?.journal.kind || null};
  }
  async withLock(gameDir,callback) {
    gameDir=await this.validateGame(gameDir); this.activeGame=gameDir;
    const lock=path.join(gameDir,META+'.lock'); await assertRegular(lock);
    if (await exists(lock)) {
      let previous;
      try { previous=await readJSON(lock); } catch { throw new Error('يوجد قفل عملية غير صالح. أغلق البرنامج السابق وأعد المحاولة.'); }
      if (!Number.isInteger(previous.pid)) throw new Error('قفل العملية غير صالح.');
      try { process.kill(previous.pid,0); throw new Error('هناك عملية أخرى تعمل على هذه اللعبة.'); }
      catch (e) { if (e.code!=='ESRCH') throw e; }
      await fs.rm(lock);
    }
    let handle;
    try { handle=await fs.open(lock,'wx'); await handle.writeFile(JSON.stringify({pid:process.pid,started:new Date().toISOString()})); }
    catch (e) { if (e.code==='EACCES' || e.code==='EPERM') throw new Error('لا توجد صلاحية للكتابة في مجلد اللعبة. على ويندوز شغّل البرنامج كمسؤول.'); throw e; }
    try { return await callback(); }
    finally { await handle.close(); await fs.rm(lock,{force:true}); this.activeGame=null; }
  }
  async ensureNoPending(c) {
    const pending=(await operations(c.meta)).find(x=>['applying','restoring'].includes(x.journal.phase));
    if (pending) throw new Error('وجدنا عملية لم تكتمل. اختر «استعادة العملية السابقة» من القائمة أولًا.');
  }
  async extract(c,options) {
    const blob=path.join(this.dataDir,'payload.bin');
    options.progress?.({phase:'verify',current:0,total:1});
    if (await hash(blob)!==c.manifest.blobHash) throw new Error('حزمة التعريب تغيرت أو لم تكتمل. أعد تنزيل البرنامج.');
    const stat=await fs.stat(blob);
    const directory=path.join(c.meta,'staging',crypto.randomUUID());
    await assertRegular(directory); await fs.mkdir(directory,{recursive:true});
    try {
      for (let i=0;i<c.manifest.files.length;i++) {
        options.checkCancel?.();
        const entry=c.manifest.files[i], p=safeJoin(directory,entry.path);
        if (entry.offset+entry.compressedSize>stat.size) throw new Error('حزمة التعريب غير مكتملة.');
        await fs.mkdir(path.dirname(p),{recursive:true});
        await pipeline(fss.createReadStream(blob,{start:entry.offset,end:entry.offset+entry.compressedSize-1}),zlib.createGunzip(),fss.createWriteStream(p,{flags:'wx'}));
        if ((await fs.stat(p)).size!==entry.size || await hash(p)!==entry.sha256) throw new Error('فشل التحقق من ملف في الحزمة.');
        options.progress?.({phase:'extract',current:i+1,total:c.manifest.files.length});
      }
      return directory;
    } catch (e) { await fs.rm(directory,{recursive:true,force:true}); throw e; }
  }
  async legacy(c) {
    const candidates=[...this.legacyAppDirs];
    if (path.basename(c.modRoot).toLowerCase()==='mod') candidates.push(path.dirname(c.modRoot));
    if (this.platform==='win32' && process.env.LOCALAPPDATA) candidates.push(path.join(process.env.LOCALAPPDATA,'KH2FM-Arabic'));
    for (const appDir of [...new Set(candidates)]) {
      const statePath=path.join(appDir,'kh2ar_state.txt');
      if (!(await exists(statePath))) continue;
      await assertRegular(statePath);
      const values={};
      for (const line of (await fs.readFile(statePath,'utf8')).replace(/^\ufeff/,'').split(/\r?\n/)) {
        const at=line.indexOf('='); if (at>0) { const key=line.slice(0,at); if (Object.hasOwn(values,key)) throw new Error('سجل المثبت القديم يحتوي قيمًا مكررة.'); values[key]=line.slice(at+1); }
      }
      if (!values.GameDir || !values.ModRoot) continue;
      let game=await windowsPathToHost(values.GameDir,c.gameDir,c.prefix,this.platform);
      let mod=await windowsPathToHost(values.ModRoot,c.gameDir,c.prefix,this.platform);
      if(await exists(game)) game=await fs.realpath(game);
      if(await exists(mod)) mod=await fs.realpath(mod);
      if (!samePath(game,c.gameDir) || !samePath(mod,c.modRoot)) continue;
      const backups=[]; const list=path.join(appDir,'kh2ar_backups.txt');
      if (await exists(list)) {
        await assertRegular(list);
        for (const line of (await fs.readFile(list,'utf8')).replace(/^\ufeff/,'').split(/\r?\n/).filter(x=>x.trim())) backups.push(await windowsPathToHost(line.trim(),c.gameDir,c.prefix,this.platform));
      }
      return {appDir,settingsOwned:values.SettingsByUs==='1',backups};
    }
    return {appDir:null,settingsOwned:false,backups:[]};
  }
  async original(c,target,entry,oldEntry,legacy) {
    if (oldEntry) return oldEntry.original;
    const current=await hash(target);
    if (!current) return null;
    let source=target;
    const backup=target+'.kh2ar.bak';
    if (legacy.backups.some(x=>samePath(x,target)) && await exists(backup)) source=backup;
    const digest=await hash(source);
    const arabic=entry.root==='mod' && this.knownArabic(entry.path.slice(4),digest);
    const oldLoader=entry.root==='game' && legacy.settingsOwned && entry.path!=='panacea_settings.txt' && this.catalog.loader.some(x=>x.path===entry.path && x.sha256===digest);
    const oldSettings=entry.path==='panacea_settings.txt' && legacy.settingsOwned && samePath(source,target);
    if (arabic || oldLoader || oldSettings) return null;
    const relative='originals/'+crypto.randomBytes(16).toString('hex')+'.bin';
    const destination=safeJoin(c.meta,relative);
    await assertRegular(destination); await fs.mkdir(path.dirname(destination),{recursive:true}); await fs.copyFile(source,destination);
    if (await hash(destination)!==digest) throw new Error('تعذر حفظ النسخة الأصلية.');
    return {path:relative,sha256:digest};
  }
  async install(gameDir,options={}) {
    return this.withLock(gameDir,async()=>{
      const c=await this.context(gameDir,options.prefixOverride); await this.ensureNoPending(c);
      if (this.platform!=='win32' && !c.prefix) throw new Error('شغّل اللعبة مرة واحدة لإنشاء بيئة Proton، أو اختر بيئة Wine من القائمة.');
      const legacy=await this.legacy(c);
      const loaderPaths=['DBGHELP.dll','version.dll']; let loaderPresent=false,existingLoader=null;
      for (const name of loaderPaths) {
        const target=path.join(c.gameDir,name), digest=await hash(target);
        if (!digest) continue;
        const bytes=await fs.readFile(target);
        if (!this.catalog.loader.some(x=>(x.path==='DBGHELP.dll') && x.sha256===digest) && !bytes.includes(Buffer.from('panacea_settings.txt'))) throw new Error('يوجد محمل مودات مختلف في مجلد اللعبة. أوقفنا التثبيت لحماية ملفاتك.');
        loaderPresent=true; existingLoader=name;
      }
      const ownsLoader=legacy.settingsOwned || !!c.state?.entries.some(x=>x.root==='game' && ['DBGHELP.dll','version.dll'].includes(x.path));
      const selectedLoader=loaderPresent && !ownsLoader ? existingLoader : this.platform==='win32' ? 'DBGHELP.dll' : 'version.dll';
      const alternateLoader=selectedLoader==='version.dll' ? 'DBGHELP.dll' : 'version.dll';
      if (!loaderPresent && !c.state) c.modRoot=path.join(c.meta,'mod');
      await assertRegular(c.modRoot);
      const total=c.manifest.files.reduce((n,x)=>n+x.size,0);
      const disk=await fs.statfs(c.gameDir);
      if (disk.bavail*disk.bsize<total*3+50*1024*1024) throw new Error('المساحة غير كافية للتثبيت والنسخة الاحتياطية. وفر نحو '+Math.ceil((total*3+50*1024*1024)/1024**3)+' جيجابايت.');
      const stage=await this.extract(c,options);
      try {
        const entries=[],actions=[];
        const old=c.state?.entries || [];
        if(ownsLoader) {
          const alternate=path.join(c.gameDir,alternateLoader),digest=await hash(alternate);
          if(digest) {
            if(!this.catalog.loader.some(x=>x.path===alternateLoader && x.sha256===digest)) throw new Error('المحمل السابق تغير؛ أوقفنا الترقية لحمايته.');
            actions.push({target:alternate,beforeHash:digest});
          }
        }
        for (const file of c.manifest.files) {
          const root=file.group==='payload' ? 'mod' : 'game';
          if(root==='game' && ['DBGHELP.dll','version.dll'].includes(file.path) && file.path!==selectedLoader) continue;
          const oldEntry=old.find(x=>x.root===root && x.path===file.path);
          if (root==='game' && loaderPresent && !ownsLoader) continue;
          const target=safeJoin(root==='mod' ? c.modRoot : c.gameDir,file.path);
          const current=await hash(target);
          if (oldEntry && current && current!==oldEntry.sha256) throw new Error('تغيّر ملف من التعريب المثبت. أوقفنا الكتابة لحماية تعديلاتك.');
          if (root==='game' && loaderPresent && current && !this.catalog.loader.some(x=>x.path===file.path && x.sha256===current)) continue;
          const entry={root,path:file.path,sha256:file.sha256,size:file.size};
          entry.original=await this.original(c,target,entry,oldEntry,legacy); entries.push(entry);
          actions.push({target,beforeHash:current,source:safeJoin(stage,file.path)});
        }
        const settingTarget=path.join(c.gameDir,'panacea_settings.txt');
        if (!loaderPresent || old.some(x=>x.path==='panacea_settings.txt') || legacy.settingsOwned) {
          const relative=settingsValue(c.gameDir,c.modRoot,c.prefix,this.platform);
          const data=Buffer.from('mod_path='+relative+'\nshow_console=false\n');
          const entry={root:'game',path:'panacea_settings.txt',sha256:hashBytes(data),size:data.length};
          const oldEntry=old.find(x=>x.path===entry.path);
          const current=await hash(settingTarget);
          if (oldEntry && current!==oldEntry.sha256) throw new Error('تغيرت إعدادات محمل المودات. أوقفنا التثبيت لحمايتها.');
          entry.original=await this.original(c,settingTarget,entry,oldEntry,legacy); entries.push(entry);
          actions.push({target:settingTarget,beforeHash:current,data});
        }
        let registry=c.state?.registry || null;
        if (this.platform!=='win32') {
          const target=path.join(c.prefix,'user.reg'); await assertRegular(target);
          const name=selectedLoader.replace('.dll','').toLowerCase(),line='"'+name+'"="native,builtin"';
          const text=await fs.readFile(target,'utf8'), beforeLine=registryValue(text,REG_SECTION,name);
          if (registry && (registry.prefix!==c.prefix || beforeLine!==registry.afterLine)) throw new Error('تغيرت إعدادات Wine منذ التثبيت. أوقفنا الكتابة لحمايتها.');
          if (beforeLine!==line) {
            registry={prefix:c.prefix,section:REG_SECTION,name,beforeLine,afterLine:line};
            actions.push({target,beforeHash:hashBytes(Buffer.from(text)),data:Buffer.from(patchRegistry(text,line,REG_SECTION,name))});
          }
        }
        const state={schema:2,version:'1.0.5',gameDir:c.gameDir,modRoot:c.modRoot,entries,registry,installedAt:new Date().toISOString()};
        const stateTarget=path.join(c.meta,'state.json');
        actions.push({target:stateTarget,beforeHash:await hash(stateTarget),data:Buffer.from(JSON.stringify(state,null,2)+'\n')});
        const context={gameDir:c.gameDir,modRoot:c.modRoot,prefix:c.prefix};
        options.progress?.({phase:'backup',current:0,total:actions.length});
        const operation=await snapshotOperation(c.meta,context,actions,'install');
        await applyOperation(operation,{...options,allowedTarget:this.allowedTarget.bind(this)});
        return {installed:true,version:'1.0.5',operationId:operation.journal.id};
      } finally { await fs.rm(stage,{recursive:true,force:true}); }
    });
  }
  async removalState(c) {
    if (c.state) return c.state;
    const legacy=await this.legacy(c); const entries=[];
    let version=null;
    for (const candidate of this.catalog.versions) {
      const anchors=candidate.files.filter(x=>/^kh2\/msg\/us\/(sys|tt|eh)\.bar$/.test(x.path));
      if (anchors.length && (await Promise.all(anchors.map(async x=>await hash(safeJoin(c.modRoot,x.path))===x.sha256))).every(Boolean)) { version=candidate; break; }
    }
    if (!version) throw new Error('لم نجد تعريبًا معروفًا في مجلد اللعبة المختار.');
    for (const file of version.files) {
      const target=safeJoin(c.modRoot,file.path), current=await hash(target);
      if (!current) continue;
      if (current!==file.sha256) throw new Error('تغيّر ملف من التعريب القديم؛ أوقفنا الحذف لحمايته.');
      const entry={root:'mod',path:file.path,sha256:file.sha256,size:file.size};
      entry.original=await this.original(c,target,entry,null,legacy); entries.push(entry);
    }
    if (legacy.settingsOwned) {
      for (const file of this.catalog.loader) {
        const target=safeJoin(c.gameDir,file.path), current=await hash(target);
        if (current!==file.sha256) continue;
        const entry={root:'game',path:file.path,sha256:current,size:file.size};
        entry.original=await this.original(c,target,entry,null,legacy); entries.push(entry);
      }
      const target=path.join(c.gameDir,'panacea_settings.txt'), current=await hash(target);
      if (current) {
        const entry={root:'game',path:'panacea_settings.txt',sha256:current,size:(await fs.stat(target)).size};
        entry.original=await this.original(c,target,entry,null,legacy); entries.push(entry);
      }
    }
    return {schema:2,version:version.version,gameDir:c.gameDir,modRoot:c.modRoot,entries,registry:null};
  }
  async remove(gameDir,options={}) {
    return this.withLock(gameDir,async()=>{
      const c=await this.context(gameDir,options.prefixOverride); await this.ensureNoPending(c);
      const state=await this.removalState(c);
      const known=new Set(state.entries.filter(x=>x.root==='mod').map(x=>safeJoin(c.modRoot,x.path)));
      const knownBackups=new Set([...known].map(x=>x+'.kh2ar.bak'));
      const otherMods=state.entries.some(x=>x.root==='mod' && x.original) || (await filesBelow(c.modRoot)).some(x=>!known.has(x) && !knownBackups.has(x));
      const actions=[];
      for (const entry of state.entries) {
        if (otherMods && entry.root==='game') continue;
        const target=safeJoin(entry.root==='mod' ? c.modRoot : c.gameDir,entry.path);
        const current=await hash(target);
        if (current && current!==entry.sha256) throw new Error('تغيّر ملف بعد التثبيت؛ أوقفنا الحذف لحماية تعديلاتك.');
        let source;
        if (entry.original) {
          source=safeJoin(c.meta,entry.original.path);
          if (await hash(source)!==entry.original.sha256) throw new Error('النسخة الأصلية تغيرت أو لم تعد موجودة؛ أوقفنا الحذف.');
        }
        if (current || source) actions.push({target,beforeHash:current,source});
      }
      if (state.registry && !otherMods) {
        const target=path.join(state.registry.prefix,'user.reg'); await assertRegular(target);
        const text=await fs.readFile(target,'utf8');
        if (registryValue(text,REG_SECTION,state.registry.name)!==state.registry.afterLine) throw new Error('تغير إعداد محمل المودات في Wine؛ أوقفنا الحذف لحمايته.');
        actions.push({target,beforeHash:hashBytes(Buffer.from(text)),data:Buffer.from(patchRegistry(text,state.registry.beforeLine,REG_SECTION,state.registry.name))});
      }
      const stateTarget=path.join(c.meta,'state.json');
      if (await exists(stateTarget)) actions.push({target:stateTarget,beforeHash:await hash(stateTarget)});
      if (!actions.length) throw new Error('لم نجد ملفات تعريب لإزالتها.');
      const context={gameDir:c.gameDir,modRoot:c.modRoot,prefix:state.registry?.prefix || c.prefix};
      options.progress?.({phase:'backup',current:0,total:actions.length});
      const operation=await snapshotOperation(c.meta,context,actions,'remove');
      await applyOperation(operation,{...options,allowedTarget:this.allowedTarget.bind(this)});
      return {installed:false,operationId:operation.journal.id,otherModsPreserved:otherMods};
    });
  }
  async undo(gameDir,options={}) {
    return this.withLock(gameDir,async()=>{
      const c=await this.context(gameDir,options.prefixOverride);
      const history=await operations(c.meta);
      const operation=history.find(x=>['applying','restoring'].includes(x.journal.phase)) || history[0];
      if (!operation || !['committed','applying','restoring'].includes(operation.journal.phase)) throw new Error('لا توجد عملية يمكن التراجع عنها.');
      if (!samePath(operation.journal.context.gameDir,c.gameDir)) throw new Error('سجل الاستعادة يعود إلى لعبة أخرى.');
      await assertRegular(operation.journal.context.modRoot);
      if (operation.journal.context.prefix) {
        const discovered=await discoverPrefix(c.gameDir,this.platform,options.prefixOverride);
        if (!discovered || !samePath(discovered,operation.journal.context.prefix)) throw new Error('بيئة Wine لا تطابق سجل الاستعادة.');
      }
      await restoreOperation(operation,this.allowedTarget.bind(this));
      return {restored:true};
    });
  }
}
module.exports={Manager,META};
