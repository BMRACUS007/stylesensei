/**
* Template Name: iLanding
* Template URL: https://bootstrapmade.com/ilanding-bootstrap-landing-page-template/
* Updated: Nov 12 2024 with Bootstrap v5.3.3
* Author: BootstrapMade.com
* License: https://bootstrapmade.com/license/
*/

(function () {
  "use strict";

  /* ------------------------------
   Apply .scrolled class on scroll
  ------------------------------ */
  function toggleScrolled() {
    const body = document.body;
    const header = document.querySelector('#header');
    if (!header) return;

    if (
      !header.classList.contains('scroll-up-sticky') &&
      !header.classList.contains('sticky-top') &&
      !header.classList.contains('fixed-top')
    ) return;

    window.scrollY > 100
      ? body.classList.add('scrolled')
      : body.classList.remove('scrolled');
  }

  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);

  /* ------------------------------
   Mobile Nav Toggle
  ------------------------------ */
  const mobileNavToggleBtn = document.querySelector('.mobile-nav-toggle');

  function mobileNavToggle() {
    document.body.classList.toggle('mobile-nav-active');
    mobileNavToggleBtn.classList.toggle('bi-list');
    mobileNavToggleBtn.classList.toggle('bi-x');
  }

  if (mobileNavToggleBtn) {
    mobileNavToggleBtn.addEventListener('click', mobileNavToggle);
  }

  /* ------------------------------
   Close mobile nav on link click
  ------------------------------ */
  document.querySelectorAll('#navmenu a').forEach(link => {
    link.addEventListener('click', () => {
      if (document.body.classList.contains('mobile-nav-active')) {
        mobileNavToggle();
      }
    });
  });

  /* ------------------------------
   Mobile dropdown toggle
  ------------------------------ */
  document.querySelectorAll('.navmenu .toggle-dropdown').forEach(toggle => {
    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      this.parentNode.classList.toggle('active');
      this.parentNode.nextElementSibling?.classList.toggle('dropdown-active');
      e.stopImmediatePropagation();
    });
  });

  /* ------------------------------
   Scroll Top Button
  ------------------------------ */
  const scrollTop = document.querySelector('.scroll-top');

  function toggleScrollTop() {
    if (!scrollTop) return;
    window.scrollY > 100
      ? scrollTop.classList.add('active')
      : scrollTop.classList.remove('active');
  }

  if (scrollTop) {
    scrollTop.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  window.addEventListener('load', toggleScrollTop);
  document.addEventListener('scroll', toggleScrollTop);

  /* ------------------------------
   AOS Init
  ------------------------------ */
  window.addEventListener('load', () => {
    if (window.AOS) {
      AOS.init({
        duration: 600,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    }
  });

  /* ------------------------------
   GLightbox
  ------------------------------ */
  if (window.GLightbox) {
    GLightbox({ selector: '.glightbox' });
  }

  /* ------------------------------
   Swiper Init
  ------------------------------ */
  function initSwiper() {
    if (!window.Swiper) return;

    document.querySelectorAll('.init-swiper').forEach(swiperEl => {
      const configEl = swiperEl.querySelector('.swiper-config');
      if (!configEl) return;

      const config = JSON.parse(configEl.innerHTML.trim());

      if (swiperEl.classList.contains('swiper-tab')) {
        initSwiperWithCustomPagination(swiperEl, config);
      } else {
        new Swiper(swiperEl, config);
      }
    });
  }

  window.addEventListener('load', initSwiper);

  /* ------------------------------
   PureCounter
  ------------------------------ */
  if (window.PureCounter) {
    new PureCounter();
  }

  /* ------------------------------
   FAQ Toggle
  ------------------------------ */
  document.querySelectorAll('.faq-item h3, .faq-item .faq-toggle')
    .forEach(el => {
      el.addEventListener('click', () => {
        el.parentNode.classList.toggle('faq-active');
      });
    });

  /* ------------------------------
   Fix Hash Scroll on Reload
  ------------------------------ */
  window.addEventListener('load', () => {
    if (!window.location.hash) return;
    const section = document.querySelector(window.location.hash);
    if (!section) return;

    setTimeout(() => {
      const offset = parseInt(getComputedStyle(section).scrollMarginTop || 0);
      window.scrollTo({
        top: section.offsetTop - offset,
        behavior: 'smooth'
      });
    }, 100);
  });

  /* ------------------------------
   Nav Scrollspy
  ------------------------------ */
  const navLinks = document.querySelectorAll('.navmenu a');

  function navmenuScrollspy() {
    navLinks.forEach(link => {
      if (!link.hash) return;
      const section = document.querySelector(link.hash);
      if (!section) return;

      const position = window.scrollY + 200;
      if (
        position >= section.offsetTop &&
        position <= section.offsetTop + section.offsetHeight
      ) {
        document.querySelectorAll('.navmenu a.active')
          .forEach(l => l.classList.remove('active'));
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });
  }

  window.addEventListener('load', navmenuScrollspy);
  document.addEventListener('scroll', navmenuScrollspy);
 document.addEventListener("DOMContentLoaded", function () {

    const navLinks = document.querySelectorAll(
      "#mainNavbar .nav-link"
    );

    const menuToggle = document.getElementById("mainNavbar");
    const bsCollapse = new bootstrap.Collapse(menuToggle, {
      toggle: false
    });

    navLinks.forEach(function (link) {

      link.addEventListener("click", function () {

        if (window.innerWidth < 1200) {
          bsCollapse.hide();
        }

      });

    });

  });
})();
