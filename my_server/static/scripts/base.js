const tmdb_key = "db254eee52d0c8fbc70d51368cd24644";
const poster_path = "https://image.tmdb.org/t/p/w94_and_h141_bestv2";
let timeout = null;

$("#sign-in").click(function (e) { 
    e.preventDefault();
    $("#sign-in-box").slideDown().focus();
});
$("#user-drop").click(function (e) { 
    e.preventDefault();
    $("#user-options-box").slideDown().focus();
});
$("#menu-bars").mousedown(function (e) { 
    e.preventDefault();
    setTimeout(() => {
        $("#main-menu").slideDown().focus();
    }, 50);
});
$(".hidden-dropdown").on("blur", function(e) {
    console.log("lost focus");
    setTimeout(() => {
        $(this).slideUp();
    }, 100);
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
    if ($("#search").val() == "") {
        $("#search-results").hide();
    } else {
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
        }, 150);
    }
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
    const max_length = 2000;
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

function showScore(score, count, show) {
    score = Math.round(score);
    switch (show) {
        case 1:
            return `#${count}`;
            break;
        case 2:
            return score;
            break;
        case 3:
            return `${score} #${count}`;
            break;
        default:
            return "";
            break;
    }
}

function movieLists() {
    $(".movie-list").each(function() {
        list = $(this);
        type = list.data("type");
        data_id = list.data("id");
        amount = list.data("amount");
        show = list.data("show_score");
        show_name = list.data("sname") ?? 1;
        $.ajax({
            async: false,
            type: "GET",
            url: "/_get_top_list",
            dataType: "json",
            data: {
                type    : type,
                data_id : data_id,
                amount  : amount
            },
            success: function (response) {
                movies = response.movies;
                for (let i = 0; i < movies.length; i++) {
                    const e = movies[i];
                    list.append(`
                    <a href="/m/${e[0].id}">
                        <div class="row movie">
                            <img src="https://image.tmdb.org/t/p/w220_and_h330_face${e[0].poster_path}" alt="${e[0].name}">
                            <div>
                                <h3>${show_name ? e[0].name : ""}</h3>
                            </div>
                            <b class="tooltip">${showScore(e[1], e[2], show)}
                            <span class="tooltiptext">#${e[2]} in <i>${response.category} movies</i>, with a <i>${response.category} movie</i> score of ${Math.round(e[1])} (${ e[3] } votes)</span>
                            </b>
                        </div>
                    </a>
                    `)
                }
            }
        });
    });
}
movieLists()