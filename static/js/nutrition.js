(() => {
  if (!window.Chart) return;
  const trend = document.getElementById('weeklyNutritionChart');
  if (trend) {
    const labels = JSON.parse(trend.dataset.labels || '[]');
    const values = JSON.parse(trend.dataset.values || '[]');
    const target = Number(trend.dataset.target || 0);
    new Chart(trend, {type:'line',data:{labels,datasets:[{label:'Calories logged',data:values,borderColor:'#32a990',backgroundColor:'#32a9901a',fill:true,tension:.35,pointRadius:3,pointBackgroundColor:'#32a990'},{label:'Estimated target',data:labels.map(()=>target),borderColor:'#e4ae76',borderDash:[5,5],borderWidth:1.5,pointRadius:0,fill:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{usePointStyle:true,boxWidth:7,font:{family:'DM Sans',size:9},color:'#87929b'}}},scales:{x:{grid:{display:false},ticks:{color:'#99a3ab',font:{family:'DM Sans',size:9}}},y:{beginAtZero:true,grid:{color:'#eef1f3'},ticks:{color:'#99a3ab',font:{family:'DM Sans',size:9},callback:(value)=>`${value} kcal`}}}}});
  }
  const macro = document.getElementById('nutritionMacroChart');
  if (macro) {
    const data = [Number(macro.dataset.protein || 0),Number(macro.dataset.carbs || 0),Number(macro.dataset.fat || 0)];
    const hasData = data.some((value)=>value>0);
    new Chart(macro,{type:'doughnut',data:{labels:['Protein','Carbohydrates','Fat'],datasets:[{data:hasData?data:[1,1,1],backgroundColor:hasData?['#35aa94','#f2b477','#8d7fe0']:['#e8edef','#e8edef','#e8edef'],borderWidth:0}]},options:{cutout:'74%',plugins:{legend:{display:false},tooltip:{enabled:hasData}},maintainAspectRatio:false}});
  }
})();
