(() => {
  if (!window.Chart) return;
  const line = document.getElementById('reportCalories');
  if (line) {
    const labels=JSON.parse(line.dataset.labels||'[]'),values=JSON.parse(line.dataset.values||'[]');
    new Chart(line,{type:'line',data:{labels,datasets:[{label:'Calories',data:values,borderColor:'#32a990',backgroundColor:'#32a9901a',fill:true,tension:.3,pointRadius:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{beginAtZero:true,grid:{color:'#eef1f3'}}}}});
  }
  const macro=document.getElementById('reportMacros');
  if(macro){const values=JSON.parse(macro.dataset.values||'[0,0,0]'),active=values.some((v)=>v>0);new Chart(macro,{type:'doughnut',data:{labels:['Protein','Carbohydrates','Fat'],datasets:[{data:active?values:[1,1,1],backgroundColor:active?['#35aa94','#f2b477','#8d7fe0']:['#e8edef','#e8edef','#e8edef'],borderWidth:0}]},options:{cutout:'75%',plugins:{legend:{display:false},tooltip:{enabled:active}},maintainAspectRatio:false}});}
})();
