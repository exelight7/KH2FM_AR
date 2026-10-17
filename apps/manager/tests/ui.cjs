'use strict';
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const {fs,path}=require('../src/paths.cjs');
const http=require('node:http');

(async()=>{
  const output=path.resolve(__dirname,'../test-results'); await fs.mkdir(output,{recursive:true});
  const root=path.resolve(__dirname,'..');
  const server=http.createServer(async(req,res)=>{
    try{
      const file=path.resolve(root,'.'+new URL(req.url,'http://localhost').pathname);
      if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
      const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.jpg':'image/jpeg','.woff2':'font/woff2'};
      res.setHeader('Content-Type',types[path.extname(file)] || 'application/octet-stream');res.end(await fs.readFile(file));
    }catch{res.writeHead(404);res.end();}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
  try {
    for(const platform of ['win32','linux','darwin']){
      const page=await browser.newPage({viewport:{width:1130,height:790},reducedMotion:'reduce'}); const errors=[];
      page.on('pageerror',e=>errors.push(e.message));
      await page.addInitScript(platform=>{
        let state=null;
        window.kh2fm={platform:async()=>({platform,version:'1.0.9'}),chooseGame:async()=>({ok:true,value:state={gameDir:platform==='win32'?'D:\\Games\\KINGDOM HEARTS -HD 1.5+2.5 ReMIX-':'/home/player/Steam/steamapps/common/KINGDOM HEARTS -HD 1.5+2.5 ReMIX-',platform,installed:false,version:null,needsPrefix:false,pendingRecovery:false,canUndo:false}}),choosePrefix:async()=>({ok:true,value:state}),run:async operation=>({ok:true,value:{result:{},inspection:state={...state,installed:operation!=='remove',version:operation!=='remove'?'1.0.9':null,canUndo:true}}}),cancel:async()=>true,onProgress:()=>{}};
      },platform);
      await page.goto('http://127.0.0.1:'+server.address().port+'/ui/index.html'); await page.evaluate(()=>document.fonts.ready);
      assert.equal(await page.locator('#install').isDisabled(),true);
      assert.equal(await page.locator('#owner-art').evaluate(img=>img.complete && img.naturalWidth>700),true);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await page.screenshot({path:path.join(output,'UI-'+platform+'.png')});
      await page.locator('#choose-game').click(); await page.waitForFunction(()=>!document.getElementById('install').disabled);
      assert.equal(await page.locator('#game-path').isVisible(),true);
      await page.locator('#install').click(); await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('جاهز'));
      await page.locator('#menu-toggle').click(); assert.equal(await page.locator('#remove').isEnabled(),true);
      await page.screenshot({path:path.join(output,'MENU-'+platform+'.png')});
      await page.locator('#remove').click(); await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('حذف'));
      await page.locator('#menu-toggle').click(); await page.locator('#undo').click(); await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('الاستعادة'));
      await page.locator('#menu-toggle').click(); await page.locator('#help').click(); assert.equal(await page.locator('#help-dialog').isVisible(),true);
      await page.locator('#close-help').click(); assert.equal(errors.length,0,errors.join('\n'));
      await page.setViewportSize({width:940,height:690}); await page.screenshot({path:path.join(output,'UI-small-'+platform+'.png')});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await page.evaluate(()=>{
        const warning={...inspection,fontCheck:{issues:['يوجد خط في مجلد التطوير له أولوية على خط التعريب.']}};
        refresh(warning);window.kh2fm.run=async()=>({ok:true,value:{result:{},inspection:warning}});
      });
      assert.match(await page.locator('#selection-text').textContent(),/مجلد التطوير/);
      await page.locator('#install').click();
      await page.waitForFunction(()=>document.getElementById('feedback-title').textContent.includes('مراجعة'));
      assert.equal(await page.locator('#feedback').evaluate(e=>e.classList.contains('error')),true);
      await page.close();
    }
    console.log('UI checks passed for Windows, Linux and macOS layouts, artwork, folder selection, install, menu removal, undo and help.');
  }finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);process.exitCode=1;});
