(() => {
  document.querySelectorAll('.water-goal-presets button').forEach((button) => button.addEventListener('click', () => {
    const input = document.querySelector('.water-goal-form input[name="goal_ml"]');
    if (input) input.value = button.dataset.goal;
  }));
  const canvas = document.getElementById('weeklyWaterChart');
  if (canvas && window.Chart) {
    const labels = JSON.parse(canvas.dataset.labels || '[]');
    const values = JSON.parse(canvas.dataset.values || '[]');
    const goal = Number(canvas.dataset.goal || 2000);
    new Chart(canvas,{type:'bar',data:{labels,datasets:[{label:'Water (ml)',data:values,backgroundColor:values.map((value)=>value>=goal?'#32a990':'#8dcfc1'),borderRadius:5,maxBarThickness:28},{type:'line',label:'Daily goal',data:labels.map(()=>goal),borderColor:'#e6b475',borderDash:[5,4],borderWidth:1.5,pointRadius:0,fill:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{usePointStyle:true,boxWidth:7,font:{family:'DM Sans',size:9},color:'#87929b'}}},scales:{x:{grid:{display:false},ticks:{color:'#99a3ab',font:{family:'DM Sans',size:9}}},y:{beginAtZero:true,grid:{color:'#eef1f3'},ticks:{color:'#99a3ab',font:{family:'DM Sans',size:9},callback:(value)=>`${value} ml`}}}}});
  }
})();
