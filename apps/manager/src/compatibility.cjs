'use strict';
const {fs, path, exists, assertRegular} = require('./paths.cjs');
const GAME_EXE = 'KINGDOM HEARTS II FINAL MIX.exe';
const APP_ID = '2552430';
const REG_SECTION = 'Software\\\\Wine\\\\AppDefaults\\\\KINGDOM HEARTS II FINAL MIX.exe\\\\DllOverrides';
const REG_LINE = '"version"="native,builtin"';

async function discoverPrefix(gameDir, platform, override) {
  if (platform === 'win32') return null;
  const candidates = override ? [path.resolve(override)] : [];
  let ancestor = gameDir;
  while (ancestor !== path.dirname(ancestor)) {
    if (path.basename(ancestor).toLowerCase() === 'drive_c') candidates.push(path.dirname(ancestor));
    if (path.basename(ancestor) === 'steamapps') candidates.push(path.join(ancestor,'compatdata',APP_ID,'pfx'));
    ancestor = path.dirname(ancestor);
  }
  for (const candidate of candidates) {
    await assertRegular(candidate);
    const file = path.join(candidate, 'user.reg');
    if (await exists(file)) {
      await assertRegular(file);
      const contents = await fs.readFile(file, 'utf8');
      if (!contents.startsWith('WINE REGISTRY Version 2')) throw new Error('مجلد بيئة اللعبة لا يحتوي سجل Wine صالحًا.');
      return candidate;
    }
  }
  return null;
}
async function windowsPathToHost(value, gameDir, prefix, platform) {
  if (platform === 'win32') return path.resolve(gameDir, value);
  if (/^[cC]:[\\/]/.test(value)) {
    if (!prefix) throw new Error('تعذر تحديد بيئة Wine لمسار التعريب الحالي.');
    let current = path.join(prefix, 'drive_c');
    for (const part of value.slice(3).split(/[\\/]/).filter(Boolean)) {
      let name = part;
      if (await exists(current)) {
        const entries = await fs.readdir(current);
        const matches = entries.filter(x => x.toLowerCase() === part.toLowerCase());
        if (matches.length > 1) throw new Error('المجلد يحتوي أسماء متشابهة لا يمكن تحديدها بأمان.');
        if (matches.length) name = matches[0];
      }
      current = path.join(current, name);
    }
    return path.resolve(current);
  }
  if (/^[zZ]:[\\/]/.test(value)) return path.resolve('/' + value.slice(3).replaceAll('\\','/'));
  if (/^[a-zA-Z]:/.test(value)) throw new Error('مسار التعريب الحالي يستخدم قرص Wine غير مدعوم.');
  return path.resolve(gameDir, value.replaceAll('\\','/'));
}
async function settingsRoot(gameDir, prefix, platform) {
  const settings = path.join(gameDir, 'panacea_settings.txt');
  if (!(await exists(settings))) return path.join(gameDir, 'mod');
  await assertRegular(settings);
  const text = await fs.readFile(settings, 'utf8');
  const values = text.replace(/^\ufeff/, '').split(/\r?\n/).filter(x => x.startsWith('mod_path='));
  if (values.length > 1) throw new Error('إعدادات محمل المودات تحتوي أكثر من مسار.');
  return windowsPathToHost(values.length ? values[0].slice(9).trim() : './mod', gameDir, prefix, platform);
}
function registryValue(text, section = REG_SECTION, name = 'version') {
  if (!['version','dbghelp'].includes(name)) throw new Error('اسم محمل المودات غير صالح.');
  let active = false, result = null;
  for (const line of text.split(/\r?\n/)) {
    const header = line.match(/^\[([^\]]+)\]/);
    if (header) active = header[1] === section;
    else if (active && line.startsWith('"'+name+'"=')) {
      if (result !== null) throw new Error('إعداد محمل المودات مكرر في سجل Wine.');
      result = line;
    }
  }
  return result;
}
function patchRegistry(text, desiredLine, section = REG_SECTION, name = 'version') {
  if (!['version','dbghelp'].includes(name)) throw new Error('اسم محمل المودات غير صالح.');
  if (!text.startsWith('WINE REGISTRY Version 2')) throw new Error('سجل Wine غير صالح.');
  const eol = text.includes('\r\n') ? '\r\n' : '\n';
  const lines = text.split(/\r?\n/); let start=-1, end=lines.length;
  for (let i=0;i<lines.length;i++) {
    const header=lines[i].match(/^\[([^\]]+)\]/);
    if (!header) continue;
    if (start>=0) { end=i; break; }
    if (header[1]===section) start=i;
  }
  if (start<0) return desiredLine === null ? text : text.replace(/\s*$/, '')+eol+eol+'['+section+']'+eol+desiredLine+eol;
  const indexes=[];
  for (let i=start+1;i<end;i++) if (lines[i].startsWith('"'+name+'"=')) indexes.push(i);
  if (indexes.length>1) throw new Error('إعداد dbghelp مكرر في سجل Wine.');
  if (indexes.length) {
    if (desiredLine===null) lines.splice(indexes[0],1);
    else lines[indexes[0]]=desiredLine;
  } else if (desiredLine!==null) lines.splice(start+1,0,desiredLine);
  return lines.join(eol);
}
module.exports = {GAME_EXE, APP_ID, REG_SECTION, REG_LINE, discoverPrefix, settingsRoot, windowsPathToHost, registryValue, patchRegistry};
