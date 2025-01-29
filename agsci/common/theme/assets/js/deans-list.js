    /*
     * jQuery.liveFilter
     *
     * Copyright (c) 2009 Mike Merritt
     *
     * Forked by Lim Chee Aun (cheeaun.com)
     *
     * https://github.com/cheeaun/jquery.livefilter
    */

    (function(jq3){
        jq3.fn.liveFilter = function(inputEl, filterEl, options){
            var defaults = {
                filterChildSelector: null,
                filter: function(el, val){
                    return jq3(el).text().toUpperCase().indexOf(val.toUpperCase()) >= 0;
                },
                before: function(){},
                after: function(){}
            };
            var options = jq3.extend(defaults, options);

            var el = jq3(this).find(filterEl);
            if (options.filterChildSelector) el = el.find(options.filterChildSelector);

            var filter = options.filter;
            jq3(inputEl).keyup(function(){
                var val = jq3(this).val();
                var contains = el.filter(function(){
                    return filter(this, val);
                });
                var containsNot = el.not(contains);
                if (options.filterChildSelector){
                    contains = contains.parents(filterEl);
                    containsNot = containsNot.parents(filterEl).hide();
                }

                options.before.call(this, contains, containsNot);

                contains.show();
                containsNot.hide();

                if (val === '') {
                    contains.show();
                    containsNot.show();
                }

                options.after.call(this, contains, containsNot);
            });
        }
    })(jq3);


    jq3(document).ready(function(jq3) {
        console.log("Starting");


        /* Implement live filtering */
        jq3('<fieldset> <legend class="hiddenStructure"><label for="livefilter-input">Search for name</label></legend> <p><input id="livefilter-input" class="filter" type="text" placeholder="Search for a name" label="Search for a name"></p> </fieldset>').insertBefore(jq3('#livefilter-list'));
        jq3('#livefilter-list').liveFilter('#livefilter-input', 'li');

        const canvas = jq3('#deansListCanvas')[0];
        const ctx = canvas.getContext('2d');
        const deansListImage = jq3('#deansListImage');
        const imageCallsToAction = jq3('.image-cta');
        const callToActionLink = jq3('.cta-download-link');
        const downloadLink = jq3('#downloadLink');
        const backgroundImageURL = jq3('#deansListImage').attr('src');
        const semester = jq3('#deansListImage').attr('data-semester');

        generateImage("Your Name Here");

        jq3('.names-list').on('click', 'li', function() {
            const name = jq3(this).text();
            const formattedName = formatName(name);
            generateImage(formattedName);

            downloadLink.removeClass('disabled');
            //downloadLink.addClass('glowing');

            imageCallsToAction.show();

            jq3('html, body').animate({
                scrollTop: jq3('#deansListImage').offset().top - 50
            }, 750);

        });

        function formatName(name) {
            const parts = name.split(', ');

            if (parts.length === 2) {
                return `${parts[1]} ${parts[0]}`;
            }
            return name;
        }

        function generateImage(name) {
            if (backgroundImageURL) {
                const background = new Image();
                background.src = backgroundImageURL;

                background.onload = function() {
                    drawCanvas(background, name);
                    drawSemester(background, semester);
                    setImageSource(name);
                };
            } else {
                drawCanvas(null, name);
                drawSemester(null, semester);
                setImageSource(name);
            }
        }

        function drawCanvas(background, name) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (background) {
                ctx.drawImage(background, 0, 0, canvas.width, canvas.height);
            } else {
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
            }

            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.letterSpacing = "2px";

            let fontSize = 80;
            ctx.font = `900 ${fontSize}px proxima-nova, sans-serif`;

            // text overflow
            while (ctx.measureText(name).width > canvas.width - 40) { // 20px padding
                fontSize--;
                ctx.font = `900 ${fontSize}px proxima-nova, sans-serif`;
            }

            ctx.fillText(name, canvas.width / 2, 790);
        }

        function drawSemester(background, name) {

            ctx.fillStyle = '#ffffff';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            ctx.shadowColor = "black";
            ctx.shadowOffsetX = 4;
            ctx.shadowOffsetY = 4;
            ctx.shadowBlur = 4;
            ctx.letterSpacing = "12px";

            let fontSize = 60;
            ctx.font = `200 ${fontSize}px Arial, proxima-nova, sans-serif`;

            ctx.fillText(name, canvas.width / 2, 540);
        }

        function setImageSource(name) {
            canvas.toBlob(function(blob) {
                const url = URL.createObjectURL(blob);

                deansListImage.attr('src', url);
                const altText = `${name} Deans List Badge`;
                deansListImage.attr('alt', altText);

                // Set the download attribute of the image's link wrapper
                const filename = `${name.replace(/ /g, '_')}_Deans_List.jpg`;
                downloadLink.attr('href', url);
                downloadLink.attr('download', filename);

                // Set the download attribute of the CTA's link wrapper
                callToActionLink.attr('href', url);
                callToActionLink.attr('download', filename);

            }, 'image/jpeg');
        }

    });
