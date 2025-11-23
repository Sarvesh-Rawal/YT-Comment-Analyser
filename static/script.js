document.addEventListener('DOMContentLoaded', () => {
  let negativeCommentsData = []; // Store negative comments

  const input = document.getElementById('url');
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
  const negativeCard = document.querySelector('.negative-card');


  function shortenTitle(title, maxLength = 20) {
    if (!title) return 'N/A';
    return title.length > maxLength ? title.slice(0, maxLength) + '…' : title;
  }

  const titleShort = document.querySelector(".title-short");
  const titleFullPopup = document.getElementById("title-full-popup");

  button.addEventListener('click', async (e) => {
    e.preventDefault();

    const videoUrl = input.value.trim();
    if (!videoUrl) {
      console.warn('No URL entered — nothing sent.');
      return;
    }

    try {
      const res = await fetch('/analyze_video', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ video_url: videoUrl })
      });

      if (!res.ok) {
        const err = await res.json();
        console.error('Error from backend:', err);
        alert('Error fetching data: ' + (err.error || 'Unknown error'));
        return;
      }

      const data = await res.json();

      // 1️⃣ Update Post Info
      // Set short title
      postTitleEl.textContent = shortenTitle(data.video_title) || 'N/A';
      // Set full title for popup
      document.getElementById("title-full-popup").textContent = data.video_title || "N/A";

      totalCommentsEl.textContent = data.summary.total_comments ?? 0;
      uploadedOnEl.textContent = data.upload_date ? new Date(data.upload_date).toISOString().split('T')[0] : 'N/A';

      // 2️⃣ Update Overview
      positiveEl.textContent = data.summary.positive ?? 0;
      neutralEl.textContent = data.summary.neutral ?? 0;
      negativeEl.textContent = data.summary.negative ?? 0;

      // Store negative comments
      negativeCommentsData = data.summary.negative_comments || [];
      console.log(data.summary.negative_comments);
      
      // negativeCommentsData = [
      //   'This is a sample negative comment 1.',
      //   'This is a sample negative comment 2.',
      //   'This is a sample negative comment 3.',
      //   'This is a sample negative comment 4.',
      //   'This is a sample negative comment 5.',
      // ];
      
      // 3️⃣ Update Charts (Base64 images from backend)
      if (data.summary.pie_chart) pieImg.src = `data:image/png;base64,${[data.summary.pie_chart]}`;
      if (data.summary.bar_chart) barImg.src = `data:image/png;base64,${data.summary.bar_chart}`;
      if (data.summary.line_chart) lineImg.src = `data:image/png;base64,${data.summary.line_chart}`;

      console.log(data);
      // console.log(data.summary.pie_chart);
    } catch (err) {
      console.error('Network or parsing error:', err);
      alert('Failed to fetch data. Check console for details.');
    }
  });

  // --- Popup Logic ---

  // Show popup when negative card is clicked
  negativeCard.addEventListener('click', () => {
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
  });


});
