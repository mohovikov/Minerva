document.addEventListener("DOMContentLoaded", function () {
  const grid = document.querySelector(".masonry-grid");
  if (!grid) return;

  imagesLoaded(grid, function () {
    new Masonry(grid, {
      itemSelector: ".masonry-item",
      percentPosition: true,
      transitionDuration: "0.2s",
    });
  });
});
