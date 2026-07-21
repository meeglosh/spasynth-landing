(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- sticky header ---------- */
  var header = document.querySelector(".site-header");
  var onScroll = function () {
    if (window.scrollY > 20) header.classList.add("is-scrolled");
    else header.classList.remove("is-scrolled");
  };
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- mobile nav ---------- */
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("main-nav");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* ---------- scroll reveal ---------- */
  var revealEls = document.querySelectorAll("[data-reveal]");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -60px 0px" }
    );
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- oscilloscope canvases ----------
     A wandering random-walk line, echoing the plugin's own
     live-telemetry scopes (see the ORGANIC CHAOS scope in the
     product screenshot). Two instances: a big faint one behind
     the hero, a small crisp one in the chaos section. */
  function makeScope(canvas, opts) {
    if (!canvas) return;
    var ctx = canvas.getContext("2d");
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var w, h, points, cursor;
    var color = opts.color || "#4fc4d6";
    var pointCount = opts.pointCount || 140;
    var speed = opts.speed || 1;
    var lineWidth = opts.lineWidth || 1.6;

    function resize() {
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function seed() {
      points = [];
      var v = h / 2;
      for (var i = 0; i < pointCount; i++) {
        v += (Math.random() - 0.5) * h * 0.18;
        v = Math.max(h * 0.08, Math.min(h * 0.92, v));
        points.push(v);
      }
      cursor = 0;
    }

    var frame = 0;
    function step() {
      frame++;
      if (frame % Math.round(3 / speed) === 0) {
        points.shift();
        var last = points[points.length - 1];
        var next = last + (Math.random() - 0.5) * h * 0.22;
        next = Math.max(h * 0.08, Math.min(h * 0.92, next));
        points.push(next);
      }

      ctx.clearRect(0, 0, w, h);
      ctx.beginPath();
      ctx.lineWidth = lineWidth;
      ctx.strokeStyle = color;
      ctx.lineJoin = "round";
      ctx.lineCap = "round";
      ctx.shadowColor = color;
      ctx.shadowBlur = opts.glow || 0;

      var step_x = w / (points.length - 1);
      for (var i = 0; i < points.length; i++) {
        var x = i * step_x;
        var y = points[i];
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      requestAnimationFrame(step);
    }

    resize();
    seed();
    window.addEventListener("resize", function () {
      resize();
      seed();
    });
    requestAnimationFrame(step);
  }

  /* ---------- hero parallax ----------
     Title/subtitle drift slightly faster than the scroll, the
     background photo lags behind, so the copy reads as a layer
     floating above the background rather than pinned to it. */
  var heroSection = document.querySelector(".hero");
  var heroCopy = document.getElementById("hero-copy");
  var heroBg = document.querySelector(".hero-bg-image");
  if (heroSection && heroCopy && heroBg && !reduceMotion) {
    var parallaxTicking = false;
    var updateParallax = function () {
      var rect = heroSection.getBoundingClientRect();
      if (rect.bottom > 0 && rect.top < window.innerHeight) {
        var scrolled = Math.max(0, -rect.top);
        heroCopy.style.transform = "translateY(" + (scrolled * -0.18) + "px)";
        heroBg.style.transform = "translateY(" + (scrolled * 0.4) + "px)";
      }
      parallaxTicking = false;
    };
    document.addEventListener(
      "scroll",
      function () {
        if (!parallaxTicking) {
          requestAnimationFrame(updateParallax);
          parallaxTicking = true;
        }
      },
      { passive: true }
    );
    updateParallax();
  }

  if (!reduceMotion) {
    makeScope(document.getElementById("chaos-scope"), {
      color: "#f08b3a",
      pointCount: 90,
      speed: 1.3,
      lineWidth: 2,
      glow: 6
    });
  }
})();
