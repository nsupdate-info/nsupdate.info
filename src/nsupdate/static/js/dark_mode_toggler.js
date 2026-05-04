(function dark_mode_toggler(){

  // we do not set up secure cookie - we trust you, you know when to use it on http
  var theme_cookie_params = {
    expires: 366,
    path: '/',
    sameSite: 'lax'
  };

  function toggle_dark_mode() {
    var html_node = document.documentElement;
    var next_theme = (html_node.getAttribute("data-bs-theme") === "dark") ? "light" : "dark";
    html_node.setAttribute("data-bs-theme", next_theme);
    Cookies.set('nsupdate_theme', next_theme, theme_cookie_params);
  }

  function init_toggler() {
    var toggler = document.querySelector(".nsupdate_dark_mode_toggler");
    if (toggler) {
      toggler.addEventListener("click", toggle_dark_mode);
    }
  }

  document.addEventListener('DOMContentLoaded', init_toggler);

})();
