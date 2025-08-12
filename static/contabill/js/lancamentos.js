(function(){
  function parseValor(v){
    if(!v) return 0;
    if(typeof v === 'string'){
      v = v.replace(/\./g,'').replace(',', '.');
    }
    var n = parseFloat(v);
    return isNaN(n) ? 0 : n;
  }
  function format(v){
    return v.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
  }
  function recalc(){
    var totalD=0, totalC=0;
    document.querySelectorAll('#itens-body tr[data-item-id]').forEach(function(row){
      var tipo = row.getAttribute('data-tipo');
      var val = parseValor(row.getAttribute('data-valor'));
      if(tipo === 'D') totalD += val; else if(tipo === 'C') totalC += val;
    });
    var dif = totalD - totalC;
    document.getElementById('total-debito').textContent = format(totalD);
    document.getElementById('total-credito').textContent = format(totalC);
    document.getElementById('total-diferenca').textContent = format(dif);
    var btn = document.getElementById('btn-salvar');
    if(btn){ btn.disabled = Math.abs(dif) > 0.0001; }
  }
  function bindRows(){
    document.querySelectorAll('#itens-body tr[data-item-id]').forEach(function(row){
      row.addEventListener('click', function(){
        document.querySelectorAll('#itens-body tr').forEach(function(r){r.classList.remove('table-active');});
        row.classList.add('table-active');
        var id = row.getAttribute('data-item-id');
        var grid = document.getElementById('grid-itens');
        var urlCC = grid.getAttribute('data-url-cc') + '?item=' + id;
        var urlProj = grid.getAttribute('data-url-projeto') + '?item=' + id;
        htmx.ajax('GET', urlCC, {target:'#grid-cc', swap:'outerHTML'});
        htmx.ajax('GET', urlProj, {target:'#grid-projeto', swap:'outerHTML'});
      });
    });
  }
  window.recalcLancamentos = function(){
    bindRows();
    recalc();
  };
  document.addEventListener('DOMContentLoaded', function(){
    window.recalcLancamentos();
  });
})();
