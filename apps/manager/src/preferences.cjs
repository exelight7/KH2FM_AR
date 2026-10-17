'use strict';
const {path,exists,readJSON,writeJSON}=require('./paths.cjs');
async function loadPreferences(file) {
  if(!await exists(file))return {};
  let value;
  try{value=await readJSON(file);}catch{return {};}
  if(!value || typeof value!=='object' || Array.isArray(value))return {};
  const valid=p=>typeof p==='string' && p.length<=4096 && path.isAbsolute(p) && !p.includes('\0');
  if(value.schema!==1 || !valid(value.gameDir) || (value.prefixOverride!==null && value.prefixOverride!==undefined && !valid(value.prefixOverride)))return {};
  const pendingVersion=typeof value.pendingVersion==='string' && /^\d+\.\d+\.\d+$/.test(value.pendingVersion) ? value.pendingVersion : null;
  return {gameDir:value.gameDir,prefixOverride:value.prefixOverride || null,pendingVersion};
}
async function savePreferences(file,value) {await writeJSON(file,{schema:1,...value});}
module.exports={loadPreferences,savePreferences};
