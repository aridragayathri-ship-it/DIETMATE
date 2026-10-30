(() => {
  const toast = document.getElementById('toast');
  let toastTimer;
  const showToast = (message) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 2200);
  };

  document.querySelectorAll('.favorite-button').forEach((button) => button.addEventListener('click', () => showToast('Open the recipe to save it to favorites')));

  document.querySelectorAll('.shopping-item input').forEach((checkbox) => checkbox.addEventListener('change', () => {
    checkbox.closest('.shopping-item').classList.toggle('checked', checkbox.checked);
    const all = [...document.querySelectorAll('.shopping-item input')];
    const checked = all.filter((item) => item.checked).length;
    const count = document.querySelector('.shopping-progress span:first-child');
    const percent = document.querySelector('.shopping-progress span:last-child');
    const fill = document.querySelector('.shopping-track>span');
    if (count) count.textContent = `${checked} of 8 items`;
    if (percent) percent.textContent = `${Math.round(checked / 8 * 100)}%`;
    if (fill) fill.style.width = `${checked / 8 * 100}%`;
    showToast(checkbox.checked ? 'Item marked as purchased' : 'Item marked as pending');
  }));

  const updateWaterWidget = (data) => {
    const amount = document.getElementById('waterAmount');
    const goalText = document.getElementById('waterGoalText');
    const fill = document.getElementById('waterProgress');
    const percent = document.getElementById('waterPercent');
    const remaining = document.getElementById('waterRemaining');
    const last = document.getElementById('lastWater');
    const cups = document.getElementById('waterCups');
    const card = document.getElementById('dashboardWater');
    if (amount) amount.innerHTML = `${Number(data.amount_ml).toLocaleString()}<span> ml</span>`;
    if (goalText) goalText.textContent = `of ${Number(data.goal_ml).toLocaleString()} ml goal`;
    if (fill) fill.style.width = `${data.percent}%`;
    if (percent) percent.textContent = `${data.percent}% completed`;
    if (remaining) remaining.textContent = `${Number(data.remaining_ml).toLocaleString()} ml left`;
    if (last) last.textContent = data.last_intake || '—';
    if (card) card.dataset.goal = data.goal_ml;
    if (cups) cups.innerHTML = Array.from({length:data.cup_count},(_,index)=>`<span class="cup ${index < data.filled_cups ? 'filled' : ''}"><i class="fa-solid fa-glass-water"></i></span>`).join('');
  };
  const postWater = async (button, payload) => {
    try {
      button.disabled = true;
      const response = await fetch(button.dataset.endpoint, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Could not update water intake');
      updateWaterWidget(data);
      showToast(payload.reset ? 'Today’s progress reset; history preserved' : 'Water intake updated');
    } catch (error) { showToast(error.message); }
    finally { button.disabled = false; }
  };
  document.getElementById('addWater')?.addEventListener('click', (event) => postWater(event.currentTarget, {amount_ml:250}));
  document.getElementById('resetWater')?.addEventListener('click', (event) => postWater(event.currentTarget, {reset:true}));

  document.getElementById('collapseSidebar')?.addEventListener('click', () => {
    document.getElementById('sidebar')?.classList.toggle('collapsed');
    document.querySelector('.main-shell')?.classList.toggle('collapsed-shell');
  });
  document.getElementById('themeToggle')?.addEventListener('click', () => document.body.classList.toggle('dark'));
  document.querySelector('.add-meal-button')?.addEventListener('click', () => showToast('Meal scheduling will be available in the meal planner phase.'));
  const search = document.getElementById('globalSearch');
  const results = document.getElementById('searchResults');
  let searchTimer;
  search?.addEventListener('input', () => {
    const query = search.value.trim().toLowerCase();
    if (!query || !results) { results?.classList.remove('show'); return; }
    clearTimeout(searchTimer);
    searchTimer = setTimeout(async () => {
      try {
        const response = await fetch(`/foods/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Search unavailable');
        const data = await response.json();
        results.innerHTML = data.results.length ? data.results.map((item) => `<a class="search-result" href="${item.url}"><i class="fa-solid fa-bowl-food"></i> &nbsp;${item.name}<small>${item.category}</small></a>`).join('') : '<div class="search-result">No foods found</div>';
      } catch (_) { results.innerHTML = '<a class="search-result" href="/foods/">Search the food database <i class="fa-solid fa-arrow-right"></i></a>'; }
      results.classList.add('show');
    }, 180);
  });
  document.addEventListener('click', (event) => { if (!event.target.closest('.search-wrap')) results?.classList.remove('show'); });

  const canvas = document.getElementById('macroChart');
  if (canvas && window.Chart) {
    const values = [Number(canvas.dataset.protein || 0), Number(canvas.dataset.carbs || 0), Number(canvas.dataset.fat || 0)];
    const hasData = values.some((value) => value > 0);
    new Chart(canvas, {type:'doughnut',data:{labels:['Protein','Carbs','Fats'],datasets:[{data:hasData ? values : [1,1,1],backgroundColor:hasData ? ['#35aa94','#f2b477','#8d7fe0'] : ['#e8edef','#e8edef','#e8edef'],borderWidth:0,hoverOffset:3}]},options:{cutout:'78%',plugins:{legend:{display:false},tooltip:{enabled:hasData}},maintainAspectRatio:false}});
  }
})();
