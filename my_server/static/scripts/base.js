const tmdb_key = "db254eee52d0c8fbc70d51368cd24644";
const poster_path = "https://image.tmdb.org/t/p/w94_and_h141_bestv2";
let timeout = null;

$("#search-results").hide();
$("#sign-in-box").hide();
$("#user-options-box").hide();
$("#main-menu").hide();

$("#sign-in").click(function (e) { 
    e.preventDefault();
    $("#sign-in-box").slideToggle();
});
$("#user-drop").click(function (e) { 
    e.preventDefault();
    $("#user-options-box").slideToggle();
});
$("#menu-bars").click(function (e) { 
    e.preventDefault();
    $("#main-menu").slideToggle();
});

$(".picture-upload-form").change(function (e) { 
    let text = "New file: " + this.value.replace("C:\\fakepath\\", "");
    $('#update-text').show().text(text);
});

//Visa sökrutan om det står något i sökfältet när det klickas
$("#search").focus(function (e) { 
    if ($(this).val() != "") {
        $("#search-results").show();
    }
});

//Fokuserad på sökfältet?
$("#search").focusout(function (e) {
    if ($("#search-results:hover").length == 0) {
        $("#search-results").hide();
    }
});

//Släpper en bokstav på sökfältet
$("#search").keyup(function (e) { 
    $("#search-results").show();
    clearTimeout(timeout);
    timeout = setTimeout(function() {
        //Get movie info based on search query
        $.ajax({
            type: "GET",
            url: "https://api.themoviedb.org/3/search/movie",
            data: {
                api_key: tmdb_key,
                language: "en-US",
                query: $("#search").val(),
                include_adult: false
            },
            dataType: "json",
            success: function (movieResponse) {
                //get people info based on search query
                $.ajax({
                    type: "GET",
                    url: "https://api.themoviedb.org/3/search/person",
                    data: {
                        api_key: tmdb_key,
                        language: "en-US",
                        query: $("#search").val(),
                        include_adult: false
                    },
                    dataType: "json",
                    success: function (personResponse) {
                        //Combine the two lists sorted by popularity score
                        let arr1 = movieResponse.results;
                        let arr2 = personResponse.results;
                        let merged = [];
                        let index1 = 0;
                        let index2 = 0;
                        let current = 0;

                        while (current < (arr1.length + arr2.length) && current < 20) {
                            if (index2 >= arr2.length || index1 >= arr1.length) {
                                break;
                            }
                            console.log(arr1[index1].popularity + " > " + arr2[index2].popularity);
                            if(arr1[index1].popularity > arr2[index2].popularity) {
                                merged[current] = arr1[index1];
                                index1++;
                            } else {
                                merged[current] = arr2[index2];
                                index2++;
                            }

                            current++;
                        }

                        $("#search-results").empty();
                        //console.log(merged);
                        let newDiv = null;
                        for (let i = 0; i < merged.length; i++) {
                            const result = merged[i];
                            if (result.gender == null) {
                                newDiv = $("<div>").html(`
                                    <a href="/m/${result.id}">
                                        <div class="searched movie">
                                            <div class="searched-img">
                                                <img src="https://image.tmdb.org/t/p/w94_and_h141_bestv2${result.poster_path}" alt="${result["original_title}"]}">
                                            </div>
                                            <div class="searched-content">
                                                <div class="searched-headline"><h4>${result.original_title}</h4> <p>(${result.release_date.slice(0, 4)})</p></div>
                                                <p>${result.overview}</p>
                                            </div>
                                        </div>
                                    </a>
                                    `);
                            } else {
                                let knownFor = result.known_for.map(a => a.original_title).join(", ");
                                newDiv = $("<div>").html(`
                                    <a href="/p/${result.id}">
                                        <div class="searched person">
                                            <div class="searched-img">
                                                <img src="https://image.tmdb.org/t/p/w94_and_h141_bestv2${result.profile_path}" alt="${result.name}">
                                            </div>
                                            <div class="searched-content">
                                                <div class="searched-headline"><h4>${result.name}</h4> <p>(${result.known_for_department})</p></div>
                                                <p>Known for: ${knownFor}</p>
                                            </div>
                                        </div>
                                    </a>
                                    `);
                            }
                            
                            $("#search-results").append(newDiv);
                        }
                    }
                });
            }
        });
    }, 250);
});


//Toggle button
$(".toggle-button").click(function () {
    if ($(this).hasClass("enabled")) {
        $(this).removeClass("enabled").addClass("disabled");
    } else {
        $(this).removeClass("disabled").addClass("enabled");
    }
    
});


//"See more" text rutor
$(".collapse-text").each( function(event) {   //Expands selection
    const max_length = 1000;
    if( $(this).html().length > max_length ) {

        // Selects text up to your limit
        var short_text = $(this).html().substr(0, max_length);

        // Selec text from your limit to the end.
        var long_text = $(this).html().substr(max_length);

        // Modified html inside of your div.
        $(this).html("<span class='short_text'>" +short_text + "</span>...<a href='#' class='view_more'>View more...</a>" + "<span class='rest_of_text' style='display: none;'>" + long_text + 
        "</span> <a href='#' class='view_less'>View less...</a>");

        //Finds the a.read_more and binds it with the click function
        $(this).find("a.view_more").click(function(event) {
            //Prevents the 'a' from changing the url
            event.preventDefault();
            //Hides the 'view more' button/link 
            $(this).hide(); 
            //Displays the rest of the text.
            $(this).parents("div").find(".rest_of_text").show();
            $(this).parents("div").find(".view_less").show();
        });

        $(this).find("a.view_less").click(function(event) {
            //Prevents the 'a' from changing the url
            event.preventDefault();
            //Hides the 'view more' button/link 
            $(this).hide(); 
            //Displays the rest of the text.
            $(this).parents("div").find(".rest_of_text").hide();
            $(this).parents("div").find(".view_more").show();
        });
    }
}); 