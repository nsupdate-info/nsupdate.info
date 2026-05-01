(function dark_mode_toggler(){

  var theme_cookie_params = {
    expires: 366,
    path: '/',
    sameSite: 'lax'
  };

  function toggle_dark_mode() {
    var htmlNode = document.documentElement;
    if (htmlNode.getAttribute("data-bs-theme") === "dark") {
      htmlNode.setAttribute("data-bs-theme", "light");
      Cookies.set('nsupdate_theme', 'light', theme_cookie_params);
    } else {
      htmlNode.setAttribute("data-bs-theme", "dark");
      Cookies.set('nsupdate_theme', 'dark', theme_cookie_params);
    }
  }

  function init_toggler() {
    var toggler = document.querySelector(".nsupdate_dark_mode_toggler");
    toggler.addEventListener("click", toggle_dark_mode);
  }

  document.addEventListener('DOMContentLoaded', init_toggler);

})();
