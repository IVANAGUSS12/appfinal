
/* shim.js: mapea google.script.run -> API */
window.google = window.google||{}; google.script = google.script || {};
(function(){
  function makeRPC(){
    const chain={_success:null,_failure:null,
      withSuccessHandler(fn){this._success=fn;return this;},
      withFailureHandler(fn){this._failure=fn;return this;},
      _call(name,args){
        const api={
          listPacientes:{m:'GET',p:'/api/patients'},
          getCalendarMonth:{m:'GET',p:'/api/calendar-month'},
          getCalendarDay:{m:'GET',p:'/api/calendar-day'},
          getStats:{m:'GET',p:'/api/stats'},
          login:{m:'POST',p:'/api/auth/login'},
          getAdjuntos:{m:'GET',p:'/api/patients/0/attachments'}
        };
        const meta=api[name]; if(!meta){(this._failure||console.error)({message:'No soportado: '+name});return;}
        const url=new URL(meta.p, location.origin), a=(args && typeof args==='object')?args:{};
        const opt={method:meta.m, headers:{}};
        if(name==='listPacientes'||name==='getStats'){
          Object.entries(a).forEach(([k,v])=>{ if(v!==undefined&&v!=='') url.searchParams.set(k,String(v)); });
        }else if(name==='getCalendarMonth'){ url.searchParams.set('desde', a.desde); url.searchParams.set('hasta', a.hasta);
        }else if(name==='getCalendarDay'){ url.searchParams.set('fechaExacta', a.fechaExacta);
        }else if(name==='login'){ opt.headers['Content-Type']='application/json'; opt.body=JSON.stringify({email:a[0]||a.email, password:a[1]||a.password}); }
        fetch(url, opt).then(async r=>{ const ct=r.headers.get('content-type')||''; const data=ct.includes('json')?await r.json():{ok:r.ok};
          if(!r.ok) throw new Error((data && data.detail)||('HTTP '+r.status)); (this._success||console.log)(data);
        }).catch(err=> (this._failure||console.error)(err));
      }
    }; return chain;
  }
  google.script.run = new Proxy({}, {get(_t,prop){ return function(...args){ const c=makeRPC(); setTimeout(()=>c._call(prop,args),0); return c; }; }});
})();
