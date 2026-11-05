// Keep reader state local; no analytics, third-party tracking, or account access.
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.rst-content img').forEach(function (image) {
    image.loading = 'lazy';
    image.decoding = 'async';
  });
});
