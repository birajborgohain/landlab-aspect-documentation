document.addEventListener("DOMContentLoaded", function () {

    let slideIndex = 1;

    function showSlides(n) {

        let slides =
            document.getElementsByClassName("slide");

        let dots =
            document.getElementsByClassName("dot");

        if (slides.length === 0) return;

        if (n > slides.length) {
            slideIndex = 1;
        }

        if (n < 1) {
            slideIndex = slides.length;
        }

        for (let i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
        }

        for (let i = 0; i < dots.length; i++) {
            dots[i].className =
                dots[i].className.replace(" active", "");
        }

        slides[slideIndex - 1].style.display = "block";

        if (dots.length > 0) {
            dots[slideIndex - 1].className += " active";
        }
    }

    window.plusSlides = function(n) {
        showSlides(slideIndex += n);
    }

    window.currentSlide = function(n) {
        showSlides(slideIndex = n);
    }

    document.addEventListener("keydown", function(e) {

        if (e.key === "ArrowRight") {
            plusSlides(1);
        }

        if (e.key === "ArrowLeft") {
            plusSlides(-1);
        }

    });

    showSlides(slideIndex);

});



