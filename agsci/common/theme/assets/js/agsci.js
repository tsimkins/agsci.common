var jq3 = $.noConflict(true);

/* replacement for old Bootstrap 3 affi */
  jq3(document).ready(function() {

  var toggleAffix = function(affixElement, scrollElement, wrapper) {
  
    var height = affixElement.outerHeight()/3, /* added /3 so the white space gap is not huge */
        top = wrapper.offset().top + 1; 
    
    if (scrollElement.scrollTop() >= top){
        wrapper.height(height);
        affixElement.addClass("affix");
    }
    else {
        affixElement.removeClass("affix");
        wrapper.height('auto');
    }
      
  };


  jq3('[data-toggle="affix"]').each(function() {
    var ele = jq3(this),
        wrapper = jq3('<div class="affix-placeholder"></div>');
    
    ele.before(wrapper);
    jq3(window).on('scroll resize', function() {
        toggleAffix(ele, jq3(this), wrapper);
    });
    
    // init
    toggleAffix(ele, jq3(window), wrapper);
  });
  
});

// need this for tabs on mobile view so that they don't go behind top sticky nav 	
jq3('.collapse').on('shown.bs.collapse', function(e) {
    var jq3card = jq3(this).closest('.card');
    jq3('html,body').animate({
        scrollTop: jq3card.offset().top - 60
    }, 500);
});

//BOOTSTRAP HOVER OR CLICK NAV
//on load, if window 992px or less, set click behavior
if (window.innerWidth <= 992) {
    //add click behavior
    jq3('[data-toggle="dropdown"]').bootstrapDropdownHover('setClickBehavior', 'default');
} else {
    //add default hover behavior
    jq3('[data-toggle="dropdown"]').bootstrapDropdownHover({});
}

//on window resize, if window 992px or less, set click behaviour
window.addEventListener('resize', function(event) {
    if (window.innerWidth <= 992) {
        //destroy previous call to script
        jq3('[data-toggle="dropdown"]').bootstrapDropdownHover('destroy');
        //add click behavior
        jq3('[data-toggle="dropdown"]').bootstrapDropdownHover('setClickBehavior', 'default');


    } else {
        //destroy previous call to script
        jq3('[data-toggle="dropdown"]').bootstrapDropdownHover('destroy');
        //add default hover behavior
        jq3('[data-toggle="dropdown"]').bootstrapDropdownHover({});
        jq3('.nav-external-link').bootstrapDropdownHover('setClickBehavior', 'disable').on('click', function() {
            if (jq3(this).attr('aria-expanded') == 'true') {
                window.location = jq3(this).attr('href');
            }
        });
    }
});

window.sr = ScrollReveal({
        reset: false
}); /* reset to false - otherwise things get weird after launching modal */
sr.reveal('.slide-down', {
    duration: 750,
    distance: '20px',
    interval: 250,
    delay: 0,
    origin: 'top'
});
sr.reveal('.fade-up', {
    opacity: 0,
    duration: 1200,
    distance: '10px',
    interval: 0,
    delay: 0,
    origin: 'bottom'
});
sr.reveal('.reveal', {
    duration: 750,
    interval: 250,
    delay: 0,
    origin: 'top'
});

jq3(function() {
    jq3('[data-toggle="tooltip"]').tooltip()
})

jq3(document).ready(function() {
    jq3('[data-toggle="popover"]').popover();
});

jq3('.popover-dismiss').popover({
    trigger: 'focus'
})