(function dark_mode_toggler(){

  function toggle_dark_mode() {
    var htmlNode = document.documentElement;
    if (htmlNode.getAttribute("data-bs-theme") === "dark") {
      htmlNode.setAttribute("data-bs-theme", "light");
      Cookies.set('nsupdate_theme', 'light');
    } else {
      htmlNode.setAttribute("data-bs-theme", "dark");
      Cookies.set('nsupdate_theme', 'dark');
    }
  }

  function init_toggler() {
    var toggler = document.querySelector(".nsupdate_dark_mode_toggler");
    toggler.addEventListener("click", toggle_dark_mode);
  }

  document.addEventListener('DOMContentLoaded', init_toggler);

})();
