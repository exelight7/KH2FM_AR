'use strict';
const fs = require('node:fs/promises');
const fss = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

async function exists(p) { try { await fs.lstat(p); return true; } catch (e) { if (e.code === 'ENOENT') return false; throw e; } }
async function assertRegular(p) {
  const absolute = path.resolve(p);
  let current = path.parse(absolute).root;
  for (const part of absolute.slice(current.length).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    try { const stat = await fs.lstat(current); if (stat.isSymbolicLink()) throw new Error('المسار يحتوي رابطًا رمزيًا. اختر المجلد الأصلي.'); }
    catch (e) { if (e.code === 'ENOENT') break; throw e; }
  }
  if (await exists(absolute)) {
    const stat = await fs.lstat(absolute);
    if (!stat.isFile() && !stat.isDirectory()) throw new Error('المسار ليس ملفًا أو مجلدًا عاديًا.');
  }
  return absolute;
}
function safeJoin(root, relative) {
  if (typeof relative !== 'string' || !relative || relative.includes('\0') || relative.includes('\\') || relative.includes(':') || relative.startsWith('/') || relative.split('/').some(x => !x || x === '.' || x === '..')) throw new Error('سجل الملفات يحتوي مسارًا غير صالح.');
  const target = path.resolve(root, ...relative.split('/'));
  if (!target.startsWith(path.resolve(root) + path.sep)) throw new Error('مسار الملف خارج المجلد المحدد.');
  return target;
}
async function hash(p) {
  await assertRegular(p);
  if (!(await exists(p))) return null;
  if (!(await fs.stat(p)).isFile()) throw new Error('يوجد مجلد في مكان ملف من ملفات التعريب.');
  const digest = crypto.createHash('sha256');
  for await (const chunk of fss.createReadStream(p)) digest.update(chunk);
  return digest.digest('hex');
}
const hashBytes = data => crypto.createHash('sha256').update(data).digest('hex');
async function readJSON(p) { await assertRegular(p); return JSON.parse(await fs.readFile(p, 'utf8')); }
async function atomicWrite(p, data) {
  await assertRegular(p); await fs.mkdir(path.dirname(p), { recursive: true });
  const temp = p + '.tmp-' + crypto.randomUUID();
  try { await fs.writeFile(temp, data, {flag:'wx'}); await fs.rename(temp, p); }
  finally { await fs.rm(temp, {force:true}); }
}
async function atomicCopy(from, to) {
  await assertRegular(from); await assertRegular(to);
  await fs.mkdir(path.dirname(to), {recursive:true});
  const temp = to + '.tmp-' + crypto.randomUUID();
  try { await fs.copyFile(from, temp, fss.constants.COPYFILE_EXCL); await fs.rename(temp, to); }
  finally { await fs.rm(temp, {force:true}); }
}
async function writeJSON(p, value) { return atomicWrite(p, JSON.stringify(value, null, 2) + '\n'); }
async function filesBelow(root) {
  if (!(await exists(root))) return [];
  await assertRegular(root);
  const result = [], queue = [root];
  while (queue.length) {
    for (const item of await fs.readdir(queue.pop(), {withFileTypes:true})) {
      const parent = item.parentPath || item.path;
      const p = path.join(parent, item.name);
      if (item.isSymbolicLink()) throw new Error('مجلد التعريب يحتوي رابطًا رمزيًا؛ لم يتغير شيء.');
      if (item.isDirectory()) queue.push(p);
      else if (item.isFile()) result.push(p);
      else throw new Error('مجلد التعريب يحتوي ملفًا غير عادي.');
      if (result.length + queue.length > 25000) throw new Error('عدد الملفات في مجلد التعريب كبير جدًا.');
    }
  }
  return result;
}
module.exports = {fs, fss, path, crypto, exists, assertRegular, safeJoin, hash, hashBytes, readJSON, atomicWrite, atomicCopy, writeJSON, filesBelow};
