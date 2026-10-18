'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const {EventEmitter}=require('node:events');
const {Updates}=require('../src/updates.cjs');
function fixture(options={}) {
  const client=new EventEmitter(),changes=[],restarts=[];
  client.checkForUpdates=async()=>{client.emit('update-available',{version:'1.0.19'});return {};};
  client.downloadUpdate=async()=>{client.emit('download-progress',{percent:34.5});client.emit('update-downloaded',{version:'1.0.19'});return ['verified-file'];};
  client.quitAndInstall=(...args)=>restarts.push(args);
  const updates=new Updates({updater:client,version:'1.0.18',changed:s=>changes.push(s),schedule:fn=>fn(),...options});
  return {client,updates,changes,restarts};
}
test('check, explicit download and verified restart use silent install and force relaunch',async()=>{
  let saved=null;const f=fixture({beforeRestart:async version=>{saved=version;}});
  assert.equal(f.client.autoDownload,false);assert.equal(f.client.autoInstallOnAppQuit,false);
  assert.equal(f.client.disableDifferentialDownload,true);assert.equal(f.client.allowPrerelease,false);
  await f.updates.check();assert.equal(f.updates.state.status,'available');assert.equal(f.restarts.length,0);
  await f.updates.download();assert.equal(f.updates.state.status,'downloaded');assert.ok(f.changes.some(x=>x.percent===34.5));
  await f.updates.restart();assert.equal(saved,'1.0.19');assert.deepEqual(f.restarts,[[true,true]]);
});
test('no update and failed checks do not permit a restart',async()=>{
  const f=fixture();f.client.checkForUpdates=async()=>{f.client.emit('update-not-available',{});return {};};
  await f.updates.check();assert.equal(f.updates.state.status,'current');
  await assert.rejects(f.updates.restart(),/انتظر تنزيل/);
  f.client.checkForUpdates=async()=>{throw new Error('offline');};
  await f.updates.check();assert.equal(f.updates.state.status,'error');assert.equal(f.restarts.length,0);
});
test('a failed or damaged download cannot be installed',async()=>{
  const f=fixture();await f.updates.check();
  f.client.downloadUpdate=async()=>{f.client.emit('error',new Error('SHA512 mismatch'));throw new Error('SHA512 mismatch');};
  await f.updates.download();assert.equal(f.updates.state.status,'error');
  await assert.rejects(f.updates.restart(),/انتظر تنزيل/);assert.equal(f.restarts.length,0);
});
test('cancelled download can be retried with a fresh cancellation token',async()=>{
  const f=fixture();await f.updates.check();let first;
  f.client.downloadUpdate=token=>{first=token;return new Promise((_,reject)=>token.onCancel(()=>{f.client.emit('error',new Error('cancelled'));reject(new Error('cancelled'));}));};
  const pending=f.updates.download();f.updates.cancel();await pending;assert.equal(f.updates.state.status,'available');
  f.client.downloadUpdate=async token=>{assert.notEqual(token,first);assert.equal(token.cancelled,false);f.client.emit('update-downloaded',{version:'1.0.19'});};
  await f.updates.download();assert.equal(f.updates.state.status,'downloaded');
});
test('game operations and concurrent updater requests are rejected during a download',async()=>{
  let busy=true;const f=fixture({isBusy:()=>busy});await assert.rejects(f.updates.check(),/انتظر/);busy=false;
  await f.updates.check();let finish;f.client.downloadUpdate=()=>new Promise(resolve=>{finish=()=>{f.client.emit('update-downloaded',{version:'1.0.19'});resolve();};});
  const pending=f.updates.download();assert.equal(f.updates.busy,true);
  await assert.rejects(f.updates.check(),/انتظر/);await assert.rejects(f.updates.download(),/انتظر/);finish();await pending;
});
test('failed preference persistence leaves the verified update ready for retry',async()=>{
  const f=fixture({beforeRestart:async()=>{throw new Error('disk read only');}});await f.updates.check();await f.updates.download();
  await assert.rejects(f.updates.restart(),/read only/);assert.equal(f.updates.state.status,'downloaded');assert.equal(f.restarts.length,0);
});
test('unpackaged and unsupported applications do not request network updates',async()=>{
  const f=fixture({supported:false});await assert.rejects(f.updates.check(),/AppImage/);assert.equal(f.updates.state.status,'unsupported');
});
