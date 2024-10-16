var jq3 = $.noConflict(true);

/* replacement for old Bootstrap 3 affix */
jq3(document).ready(function() {

    //caches a jQuery object containing the header element
    var bttbtn = jq3(".back-to-top");

    jq3(window).scroll(function() {
        var scroll = jq3(window).scrollTop();

        if (scroll >= 1000) {
            bttbtn.removeClass('btn-hidden').addClass("btn-show");
        } else {
            bttbtn.removeClass("btn-show").addClass('btn-hidden');
        }
    });

    var toggleAffix = function(affixElement, scrollElement, wrapper) {

        var height = affixElement.outerHeight(),
            top = wrapper.offset().top + 2;

        if (scrollElement.scrollTop() >= top){
            wrapper.height(height);
            affixElement.addClass("affix");
        }
        else {
            affixElement.removeClass("affix");
            wrapper.height('auto');
        }

    };

    jq3('body.userrole-anonymous [data-toggle="affix"]').each(function() {

        if (! jq3('body.portaltype-agsci_accordion_folder, #parent-fieldname-text.pat-autotoc').length) {
            var ele = jq3(this),
                wrapper = jq3('<div class="affix-placeholder"></div>');
    
            ele.before(wrapper);
    
            jq3(window).on('scroll resize', function() {
                toggleAffix(ele, jq3(this), wrapper);
            });
    
            // init
            toggleAffix(ele, jq3(window), wrapper);
        }
    });

});

// need this for tabs on mobile view so that they don't go behind top sticky nav
jq3('.collapse').on('shown.bs.collapse', function(e) {
    var jq3card = jq3(this).closest('.card');
    jq3('html,body').animate({
        scrollTop: jq3card.offset().top - 60
    }, 500);
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

// Faceted load
jq3(document).ready(function() {

    if (typeof Faceted !== 'undefined') {

        jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS , function() {

        // Slide In Panel - by CodyHouse.co (adapted to jQuery)
        // open panel when clicking on trigger btn
        jQuery('.js-cd-panel-trigger').click(

            function (event) {

                var data_panel = jQuery(this).attr('data-panel');
                var panelClass = 'js-cd-panel-' + data_panel;

                jQuery('.' + panelClass).addClass('cd-panel--is-visible');

                //close panel when clicking on 'x' or outside the panel
                jQuery('.' + panelClass).click(
                    function(event) {

                        var target = jQuery(event.target);

                        if( target.hasClass('js-cd-close') || target.hasClass(panelClass)) {
                            event.preventDefault();
                            jQuery(this).removeClass('cd-panel--is-visible');
                        }
                    }
                );

                event.preventDefault();
            }
        );

            jQuery('body.portaltype-agsci_degree_container form.degree-explorer').each(

                function() {

                    if ( ! jQuery(".comparison-wrapper").length ) {

                        // Create wrapper div
                        var cw = jQuery("<div class='comparison-wrapper'></div>");

                        // Hide them
                        cw.hide();

                        // Add to the top and bottom of the body.
                        jQuery('body').prepend(cw);
                    }

                    // Don't submit when clicking Compare
                    jQuery(this).attr('onsubmit', 'return false;');

                    // When you actually click the submit button, go grab the results
                    // of the comparison view, and stuff that into the comparison
                    // wrapper.
                    jQuery(this).find('.compare-selections button').click(
                        function () {

                            // Get the results of the form submit and
                            // stuff them inside a div.

                            var results_url = jQuery(this).attr('data-compare-view')

                            var get_results = jQuery.get(results_url, function(data) {

                                jQuery('.comparison-wrapper').html(data);

                                jQuery('.comparison-wrapper').show('slide',
                                    { direction: 'down' },
                                    function () {
                                        jQuery('.comparison-wrapper, .comparison-container, .close-comparison-bar, .visual-cards-imgs-cropped').css({'position' : 'fixed'});
                                    }
                                );

                                jQuery('.close-comparison-bar button').each(
                                    function () {
                                        jQuery(this).click(
                                            function () {

                                                jQuery('.comparison-container, .close-comparison-bar').css({'position' : 'absolute'});
                                                jQuery('.visual-cards-imgs-cropped').css({'position' : 'static'});

                                                jQuery('.comparison-wrapper').hide('slide',
                                                    { direction: 'down' });
                                            }
                                        );
                                    }
                                );
                            });
                        }
                    );

                    jQuery(this).find('input[type="checkbox"]').change(
                        function () {

                            jQuery(this).parents('form').each(
                                function () {
                                    var degree_ids = [];

                                    jQuery(this).find('input[type="checkbox"]:checked').each(
                                        function () {
                                            degree_ids.push(jQuery(this).attr('value'));
                                        }
                                    );

                                    var compare_view = window.location.pathname + '/@@degree_compare_lightbox?degree_id=' + degree_ids.join('&degree_id=');

                                    var button = jQuery(this).find('.compare-selections button');

                                    button.attr('data-compare-view', compare_view);

                                    if (degree_ids.length >= 2) {
                                        button.attr('aria-disabled', 'false');
                                        button.toggleClass('disabled', false);
                                    }
                                    else {
                                        button.attr('aria-disabled', 'true');
                                        button.toggleClass('disabled', true);
                                    }

                                    if (degree_ids.length >= 3) {
                                        jQuery(this).find('input[type="checkbox"]:not(:checked)').prop('disabled', true);
                                        jQuery(this).find('input[type="checkbox"]:not(:checked)').parent('div.checkbox').toggleClass('disabled', true);
                                    }
                                    else {
                                        jQuery(this).find('input[type="checkbox"]').prop('disabled', false);
                                        jQuery(this).find('input[type="checkbox"]').parent('div.checkbox').toggleClass('disabled', false);

                                    }

                                }
                            );
                        }
                    );
            });

        });
    }

});

// Mosaic fixes

jq3(document).ready(function() {

    // Add a class of .container to any mosiac-tile-row that has a child of .container
    // This fixes multi-column mosaic layout issues

    jq3('.mosaic-grid-row:not(:has(section[data-container-width="full"]))').each(
        function () {
            jq3(this).addClass('container');
        }
    );

    jq3('.mosaic-grid-row:has(section[data-container-width="not-full"])').each(
        function () {
            jq3(this).addClass('container');
        }
    );

    // Add margin class for sections that are inside a first 3/4 width cell
    jq3('.mosaic-grid-cell.mosaic-position-leftmost.mosaic-width-three-quarters section').each(
        function() {
            jq3(this).addClass('mr-lg-5').removeClass('container');
        }
    );

    // Move navigation portlet on homepage into its own row above.
    jq3('.mosaic-grid-row .navigation-wrapper').each(
        function() {

            var nav_wrapper = jq3(this);

            jq3(this).parents('.mosaic-grid-row').each(
                function () {

                    var new_cell = jq3('<div class="mosaic-grid-cell mosaic-navigation"></div>')
                    nav_wrapper.addClass('mt-3');
                    nav_wrapper.appendTo(new_cell);
                    new_cell.prependTo(jq3(this));
                }
            );
        }
    );
});


// Expand the nav portlet on page load.

jq3(document).ready(function() {
    jq3('#navbarSectionNav li.navTreeCurrentItem > ul, #navbarSectionNav li.navTreeItemInPath > ul, #navbarSectionNav li.navTreeCurrentNode > ul').each(
        function () {
            jq3(this).addClass('show');
        }
    );

    jq3('#navbarSectionNav li.navTreeCurrentItem > button, #navbarSectionNav li.navTreeItemInPath > button, #navbarSectionNav li.navTreeCurrentNode > button').each(
        function () {
            jq3(this).attr('aria-expanded', true);
        }
    );
});

//BOOTSTRAP HOVER OR CLICK NAV
//on load, if window 992px or less, set click behavior
if(window.innerWidth <= 992){
    mobileHover();
}else{
    desktopHover();
}

//on window resize, if window 992px or less, set click behaviour
window.addEventListener('resize', function(event){
    if(window.innerWidth <= 992){
        mobileHover();
    }else{
        desktopHover();
    }
});

function mobileHover(){
    jq3('header [data-toggle="dropdown"]').bootstrapDropdownHover('destroy');
    jq3('header [data-toggle="dropdown"]').bootstrapDropdownHover('setClickBehavior', 'default');
}

function desktopHover(){

    //destroy previous call to script
    jq3('header [data-toggle="dropdown"]').bootstrapDropdownHover('destroy');

    jq3('header [data-toggle="dropdown"]').bootstrapDropdownHover();

    //enable click behavior on external links only
    jq3('header .nav-external-link').bootstrapDropdownHover('setClickBehavior', 'enable');

    //on "click" and expanded, then go to link
    jq3('header .nav-external-link').on('click', function(){
        if (jq3(this).attr('aria-expanded')=='true') {
            window.location = jq3(this).attr('href');
        }
    });
}

// Prevent multiple PFG form submissions
// https://gist.github.com/toddlahman/6302114
jq3('body.portaltype-formfolder .pfg-form form').submit(function(){
    jq3(this).find(':submit').attr( 'disabled','disabled' );
});

/* Lazy load images */
jq3(document).ready(function() {
    jq3('img').each(function () {

        // If it has a data-src, set the src

        var _src = jq3(this).attr('data-src');

        if (_src) {
            jq3(this).attr('src', _src);
        }

    });

});

/* Scroll to anchor in accordion */
jq3(document).ready(function() {
    if (window.location.hash) {
        jq3("body.portaltype-agsci_accordion_folder " + window.location.hash + " div.accordion-collapse").each(function () {
            jq3(this).addClass("show");
            jq3(this).removeClass("hide");
        })

        jq3('html, body').scrollTop(jq3(window.location.hash).offset().top);
    }

    console.log(window.location);
});
