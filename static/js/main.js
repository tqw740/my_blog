// 每次发布【新】公告时，修改这里的版本号（例如更新为 'v2' 或日期）
const CURRENT_BANNER_ID = 'banner_v2';

// 页面加载完成后检查是否已关闭过
document.addEventListener('DOMContentLoaded', () => {
  const isClosed = localStorage.getItem('closed_announcement_id');
  const bar = document.getElementById('top-announcement-bar');

  // 如果用户之前没关闭过这个版本的通告，才展示
  if (isClosed !== CURRENT_BANNER_ID && bar) {
    bar.style.display = 'block';
  }
});

// 点击关闭按钮的动作
function closeTopAnnouncement() {
  const bar = document.getElementById('top-announcement-bar');
  if (bar) {
    bar.style.display = 'none';
  }
  // 记录到本地，该版本的通告不会再显示
  localStorage.setItem('closed_announcement_id', CURRENT_BANNER_ID);
}