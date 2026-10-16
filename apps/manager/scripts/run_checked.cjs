'use strict';
const {spawnSync}=require('node:child_process');
const {fs,path}=require('../src/paths.cjs');
const [command,...args]=process.argv.slice(2);
const result=spawnSync(command,args,{encoding:'utf8',shell:process.platform==='win32',maxBuffer:30*1024*1024});
const output=(result.stdout || '')+(result.stderr || '')+(result.error?.message || '');
process.stdout.write(output);
if(result.status!==0) console.log('::error::'+output.slice(-5500).replaceAll('%','%25').replaceAll('\r','%0D').replaceAll('\n','%0A'));
if(command==='npm' && args[0]==='test') {
  require('node:fs').mkdirSync('test-results',{recursive:true});
  require('node:fs').writeFileSync(path.join('test-results','CORE-'+process.platform+'-'+process.arch+'.txt'),output);
}
process.exit(result.status ?? 1);
