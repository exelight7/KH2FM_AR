'use strict';
const {fs,path,exists,assertRegular,safeJoin,hash,filesBelow}=require('./paths.cjs');
const {windowsPathToHost}=require('./compatibility.cjs');
const FONT_FOLDER='kh2/remastered/msg/us/fontimage.bar';
const FONT_FILES=['kh2/msg/us/fontimage.bar','kh2/msg/us/fontinfo.bar',...Array.from({length:3},(_,i)=>FONT_FOLDER+'/US_fontimage_bar'+i+'.png')];
function conflictPath(relative) {
  return relative.startsWith(FONT_FOLDER+'/') && /\.(png|dds)$/i.test(relative) && !FONT_FILES.includes(relative);
}
async function extraImages(modRoot) {
  const folder=safeJoin(modRoot,FONT_FOLDER);
  return (await filesBelow(folder)).map(p=>path.relative(modRoot,p).split(path.sep).join('/')).filter(p=>conflictPath(p) && (process.platform!=='win32' || !FONT_FILES.some(x=>x.toLowerCase()===p.toLowerCase())));
}
async function loaderPaths(gameDir,prefix,platform) {
  const file=path.join(gameDir,'panacea_settings.txt'),values={mod_path:'./mod'};
  await assertRegular(file);
  if(await exists(file)) {
    const seen=new Set();
    // Panacea uses exact keys and untrimmed UTF-8 values. A BOM does not
    // disappear in its fgets parser; the first key then remains unrecognized.
    for(const line of (await fs.readFile(file,'utf8')).split(/\r?\n/)) {
      const at=line.indexOf('='),key=line.slice(0,at),value=line.slice(at+1);
      if(at<1 || !['mod_path','dev_path','extract_path'].includes(key) || !value) continue;
      if(seen.has(key)) throw new Error('إعدادات محمل المودات تحتوي مسارًا مكررًا: '+key);
      seen.add(key);values[key]=value;
    }
  }
  const result={};
  for(const [key,value] of Object.entries(values)) {
    const root=await windowsPathToHost(value,gameDir,prefix,platform);
    await assertRegular(root);
    result[key]=await exists(root) ? await fs.realpath(root) : root;
  }
  return result;
}
async function fontReport(c,platform) {
  const expected=c.manifest.files.filter(x=>FONT_FILES.includes(x.path));
  const roots=await loaderPaths(c.gameDir,c.prefix,platform);
  const files=[];
  for(const file of expected) files.push({path:file.path,expected:file.sha256,actual:await hash(safeJoin(c.modRoot,file.path))});
  const extras=await extraImages(c.modRoot),issues=[];
  const equal=(a,b)=>platform==='win32' ? a.toLowerCase()===b.toLowerCase() : a===b;
  const pathMismatch=!equal(roots.mod_path,c.modRoot);
  if(pathMismatch) issues.push('إعدادات اللعبة تشير إلى مجلد مودات مختلف عن مجلد التعريب المثبت.');
  const developmentOverride=!!roots.dev_path && !equal(roots.dev_path,c.modRoot) && (await exists(safeJoin(roots.dev_path,'kh2/msg/us/fontimage.bar')) || await exists(safeJoin(roots.dev_path,FONT_FOLDER)) || await exists(safeJoin(roots.dev_path,'kh2/msg/us/fontinfo.bar')));
  if(developmentOverride) issues.push('يوجد خط في مجلد التطوير له أولوية على خط التعريب.');
  if(extras.length) issues.push('توجد صور خط إضافية قد تتقدم على الخط الجديد؛ إعادة التثبيت تحفظها وتعطل تعارضها.');
  if(c.state && files.some(x=>x.actual!==x.expected)) issues.push('ملفات الخط المثبتة لا تطابق خط هذه الحزمة.');
  return {installedRoot:c.modRoot,loaderRoots:roots,files,extraImages:extras,pathMismatch,developmentOverride,issues};
}
module.exports={FONT_FOLDER,conflictPath,extraImages,loaderPaths,fontReport};
