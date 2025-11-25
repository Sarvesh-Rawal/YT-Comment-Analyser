document.addEventListener('DOMContentLoaded', () => {
  let positiveCommentsData = []; // Store positive comments
  let neutralCommentsData = []; // Store neutral comments
  let negativeCommentsData = []; // Store negetive comments

  const input = document.getElementById('url');
  input.focus();
  input.select();
  const button = document.getElementById('analyze-btn');

  // Post info elements
  const postTitleEl = document.querySelector('.post-info .info-card:nth-child(2) p');
  const totalCommentsEl = document.querySelector('.post-info .info-card:nth-child(3) p');
  const uploadedOnEl = document.querySelector('.post-info .info-card:nth-child(4) p');

  // Overview elements
  const positiveEl = document.querySelector('.positive-card .value');
  const neutralEl = document.querySelector('.neutral-card .value');
  const negativeEl = document.querySelector('.negative-card .value');

  // Chart image elements
  const pieImg = document.getElementById('pieChart');
  const barImg = document.getElementById('barChart');
  const lineImg = document.getElementById('lineChart');

  // Popup elements
  const commentsPopup = document.getElementById('comments-popup');
  const popupCloseBtn = document.getElementById('popup-close');
  const commentsListEl = document.getElementById('popup-comments-list');
  const positiveCard = document.querySelector('.positive-card');
  const neutralCard = document.querySelector('.neutral-card');
  const negativeCard = document.querySelector('.negative-card');
  const popupTitleEl = document.getElementById('popup-title');


  function shortenTitle(title, maxLength = 20) {
    if (!title) return 'N/A';
    return title.length > maxLength ? title.slice(0, maxLength) + '…' : title;
  }

  const titleShort = document.querySelector(".title-short");
  const titleFullPopup = document.getElementById("title-full-popup");

  // Trigger analyze button on Enter key press in the input field
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      event.preventDefault();
      button.click();
    }
  });

  button.addEventListener('click', async (e) => {
    e.preventDefault();
    console.log("analyzing");

    const videoUrl = input.value.trim();
    if (!videoUrl) {
      console.warn('No URL entered — nothing sent.');
      return;
    }

    // All sections except input area
    const postInfo = document.querySelector('.post-info');
    const overview = document.querySelector('.overview');
    const charts = document.querySelector('.charts');
    const footer = document.querySelector('footer');

    const spinner = document.getElementById('loading-spinner');

    // Hide everything except input section
    postInfo.classList.add('hide');
    overview.classList.add('hide');
    charts.classList.add('hide');
    footer.classList.add('hide');

    // Show loading spinner
    spinner.classList.remove('hidden');

    try {
      const res = await fetch('/analyze_video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: videoUrl })
      });

      if (!res.ok) {
        const err = await res.json();
        alert('Error fetching data: ' + (err.error || 'Unknown error'));
        return;
      }

      const data = await res.json();

      // Update title
      postTitleEl.textContent = shortenTitle(data.video_title) || 'N/A';
      document.getElementById("title-full-popup").textContent = data.video_title || "N/A";

      // Update info
      totalCommentsEl.textContent = data.summary.total_comments ?? 0;
      uploadedOnEl.textContent = data.upload_date
        ? new Date(data.upload_date).toISOString().split('T')[0]
        : 'N/A';

      // Update overview
      positiveEl.textContent = data.summary.positive ?? 0;
      neutralEl.textContent = data.summary.neutral ?? 0;
      negativeEl.textContent = data.summary.negative ?? 0;

      // Store comments
      positiveCommentsData = data.summary.positive_comments || [];
      neutralCommentsData = data.summary.neutral_comments || [];
      negativeCommentsData = data.summary.negative_comments || [];

      // Update charts
      if (data.summary.pie_chart) pieImg.src = `data:image/png;base64,${data.summary.pie_chart}`;
      if (data.summary.bar_chart) barImg.src = `data:image/png;base64,${data.summary.bar_chart}`;
      if (data.summary.line_chart) lineImg.src = `data:image/png;base64,${data.summary.line_chart}`;

    } catch (err) {
      console.error('Network or parsing error:', err);
      alert('Failed to fetch data. Check console for details.');
    }

    // Restore UI after loading
    spinner.classList.add('hidden');

    postInfo.classList.remove('hide');
    overview.classList.remove('hide');
    charts.classList.remove('hide');
    footer.classList.remove('hide');
  });


  // --- Popup Logic ---
  // Show popup when Positive card is clicked
  positiveCard.addEventListener('click', () => {
    popupTitleEl.textContent = "Positive Comments";
    document.body.style.overflow = "hidden"; //Disables background window scroll
    if (positiveCommentsData.length > 0) {
      commentsListEl.innerHTML = ''; // Clear previous comments
      positiveCommentsData.forEach(comment => {
        const li = document.createElement('li');
        li.textContent = comment;
        commentsListEl.appendChild(li);
      });
      commentsPopup.classList.add('show');
    } else {
      alert('No positive comments to display or data not loaded yet.');
    }
  });

  // Show popup when Neutral card is clicked
  neutralCard.addEventListener('click', () => {
    popupTitleEl.textContent = "Neutral Comments";
    document.body.style.overflow = "hidden"; //Disables background window scroll
    if (neutralCommentsData.length > 0) {
      commentsListEl.innerHTML = ''; // Clear previous comments
      neutralCommentsData.forEach(comment => {
        const li = document.createElement('li');
        li.textContent = comment;
        commentsListEl.appendChild(li);
      });
      commentsPopup.classList.add('show');
    } else {
      alert('No neutral comments to display or data not loaded yet.');
    }
  });

  // Show popup when Negetive card is clicked
  negativeCard.addEventListener('click', () => {
    popupTitleEl.textContent = "Negative Comments";
    document.body.style.overflow = "hidden"; //Disables background window scroll
    if (negativeCommentsData.length > 0) {
      commentsListEl.innerHTML = ''; // Clear previous comments
      negativeCommentsData.forEach(comment => {
        const li = document.createElement('li');
        li.textContent = comment;
        commentsListEl.appendChild(li);
      });
      commentsPopup.classList.add('show');
    } else {
      alert('No negative comments to display or data not loaded yet.');
    }
  });

  // Hide popup when close button is clicked
  popupCloseBtn.addEventListener('click', () => {
    commentsPopup.classList.remove('show');
    document.body.style.overflow = "auto"; //Enables background window scroll
  });

  // Close popup when clicking outside the popup content
  commentsPopup.addEventListener('click', (e) => {
    if (e.target === commentsPopup) {
      commentsPopup.classList.remove('show');
      document.body.style.overflow = "auto"; //Enables background window scroll
    }
  });

  // Close popup when pressing ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === "Escape") {
      commentsPopup.classList.remove('show');
      document.body.style.overflow = "auto"; //Enables background window scroll
    }
  });

});
