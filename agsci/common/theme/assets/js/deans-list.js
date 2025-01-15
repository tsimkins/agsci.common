    jq3(document).ready(function($) {

        const canvas = jq3('#deansListCanvas')[0];
        const ctx = canvas.getContext('2d');
        const deansListImage = jq3('#deansListImage');
        const imageCallsToAction = jq3('.image-cta');
        const callToActionLink = jq3('.cta-download-link');
        const downloadLink = jq3('#downloadLink');
        const backgroundImageURL = jq3('#deansListImage').attr('src');

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
                    setImageSource(name);
                };
            } else {
                drawCanvas(null, name);
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

            let fontSize = 80;
            ctx.font = `900 ${fontSize}px proxima-nova, sans-serif`;
            
            // text overflow
            while (ctx.measureText(name).width > canvas.width - 40) { // 20px padding
                fontSize--;
                ctx.font = `900 ${fontSize}px proxima-nova, sans-serif`;
            }
            
            ctx.fillText(name, canvas.width / 2, 785);
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
