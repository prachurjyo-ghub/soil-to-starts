import path from 'node:path';
import { spawn } from 'node:child_process';
import { InputError,validateIntake } from './intake-validation.mjs';
const root=path.resolve(process.cwd(),'..');
const noStore={'cache-control':'no-store','x-content-type-options':'nosniff'};
let running=0;
export function json(body,status=200){return Response.json(body,{status,headers:noStore});}
function localRequest(request){
 const url=new URL(request.url),host=request.headers.get('host')||url.host;
 if(!/^(localhost|127\.0\.0\.1|\[::1\])(?::\d+)?$/.test(host))return false;
 const origin=request.headers.get('origin');
 if(origin){try{if(new URL(origin).host!==host)return false;}catch{return false;}}
 return true;
}
export async function readJSON(request){
 if(!request.headers.get('content-type')?.toLowerCase().startsWith('application/json'))throw new InputError('Use application/json');
 if(Number(request.headers.get('content-length')||0)>65536)throw new InputError('Input exceeds 64KB');
 const reader=request.body?.getReader();if(!reader)throw new InputError('Empty request');
 let bytes=0;const chunks=[];
 while(true){const {value,done}=await reader.read();if(done)break;bytes+=value.byteLength;if(bytes>65536){await reader.cancel();throw new InputError('Input exceeds 64KB');}chunks.push(value);}
 try{return JSON.parse(Buffer.concat(chunks).toString('utf8'));}catch{throw new InputError('Invalid JSON');}
}
export function service(message){
 if(running>=4)return Promise.resolve({http_status:503,body:{status:'error',reason:'Local service is busy. Please retry.',recoverable:true}});
 running++;
 return new Promise(resolve=>{
  let finished=false,out='',err='';
  const child=spawn(process.env.STS_PYTHON||'python3',['-B',path.join(root,'src/api/local_service.py')],{cwd:root,env:process.env,stdio:['pipe','pipe','pipe']});
  const done=value=>{if(finished)return;finished=true;clearTimeout(timer);running--;resolve(value);};
  const timer=setTimeout(()=>{child.kill();done({http_status:503,body:{status:'error',reason:'Local evidence processing timed out. Retry after checking setup.',recoverable:true}});},25000);
  child.stdout.on('data',chunk=>{out+=chunk;if(Buffer.byteLength(out)>2*1024*1024){child.kill();done({http_status:503,body:{status:'error',reason:'Local result exceeded the response limit.'}});}});
  child.stderr.on('data',chunk=>{if(err.length<2048)err+=chunk;});
  child.on('error',()=>done({http_status:503,body:{status:'error',reason:'Python could not start. Install Python 3.9+ or set STS_PYTHON.',recoverable:true}}));
  child.on('close',()=>{if(finished)return;try{const result=JSON.parse(out);if(!result.body||!Number.isInteger(result.http_status))throw Error();done(result);}catch{done({http_status:503,body:{status:'error',reason:'Local evidence processing failed. Check the local setup.',recoverable:true}});}});
  child.stdin.on('error',()=>{});child.stdin.end(JSON.stringify(message));
 });
}
export async function post(request,operation){
 if(!localRequest(request))return json({status:'invalid_input',reason:'Only same-origin localhost requests are accepted.'},403);
 try{
  const raw=await readJSON(request),clean=validateIntake(raw.intake||raw);
  const result=await service({operation,intake:clean,kind:raw.request_kind==='scenario'?'scenario':'field'});
  return json(result.body,result.http_status);
 }catch(error){if(error instanceof InputError)return json({status:'invalid_input',reason:error.message,errors:error.errors},422);return json({status:'error',reason:'Local input validation could not run. Check the local assets.'},503);}
}
export async function get(request,operation,id){
 if(!localRequest(request))return json({status:'invalid_input',reason:'Only localhost requests are accepted.'},403);
 if(id&&!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/.test(id))return json({status:'not_found'},404);
 const result=await service({operation,id});return json(result.body,result.http_status);
}
