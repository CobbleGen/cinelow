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
$("#menu-bars").click(function (e) { 
    e.preventDefault();
    $("#main-menu").slideDown().focus();
});
$(".hidden-dropdown").on("blur", function(e) {
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
                                if (arr2.length < 1 || arr1.length < 1) {
                                    merged = merged.concat(arr1);
                                    merged = merged.concat(arr2);
                                    break;
                                }
                                if(arr1[0].popularity > arr2[0].popularity) {
                                    merged[current] = arr1.shift();
                                    index1++;
                                } else {
                                    merged[current] = arr2.shift();
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
                                                    <img src="https://image.tmdb.org/t/p/w94_and_h141_bestv2${result.poster_path}" alt="${result["title}"]}">
                                                </div>
                                                <div class="searched-content">
                                                    <div class="searched-headline"><h4>${result.title}</h4> <p>(${result.release_date.slice(0, 4)})</p></div>
                                                    <p>${result.overview}</p>
                                                </div>
                                            </div>
                                        </a>
                                        `);
                                } else {
                                    let knownFor = result.known_for.map(a => a.title).join(", ");
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
        $(this).removeClass("enabled").addClass("crossed").children("span").html("<h4>Not seen.</h4>");
        clearTimeout(timeout);
        timeout = setTimeout(sendSeenMovie(-1), 2500);
    } else {
        $(this).removeClass("disabled").removeClass("crossed").addClass("enabled").children("span").html("<h4>Seen.</h4>");
        clearTimeout(timeout);
        timeout = setTimeout(sendSeenMovie(1), 2500);
    }
});

function sendSeenMovie(seen) {
    $.ajax({
        type: "POST",
        url: "/_seen_movie",
        data: {
            movie_id: $("#movie-data").data("id"),
            seen_value : seen
        },
        success: function (response) {
            
        }
    });
}


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
        case 2:
            return score;
        case 3:
            return `${score} #${count}`;
        default:
            return "";
    }
}

function displayLists(movies, list, show, show_name, category) {
    for (let i = 0; i < movies.length; i++) {
        const e = movies[i];
        if(category != "rec") {
            list.append(`
            <a href="/m/${e[0].id}">
                <div class="row movie">
                    <img src="https://image.tmdb.org/t/p/w220_and_h330_face${e[0].poster_path}" alt="${e[0].name}">
                    <div>
                        <h3>${show_name ? e[0].name : ""}</h3>
                    </div>
                    <b class="tooltip">${showScore(e[1], e[2], show)}
                    <span class="tooltiptext">#${e[2]} in <i>${category} movies</i>, with a <i>${category} movie</i> score of ${Math.round(e[1])} (${ e[3] } votes)</span>
                    </b>
                </div>
            </a>
            `)
        } else {
            list.append(`
            <a href="/m/${e.id}">
                <div class="row movie">
                    <img src="https://image.tmdb.org/t/p/w220_and_h330_face${e.poster_path}" alt="${e.name}">
                    <div>
                        <h3>${show_name ? e.name : ""}</h3>
                    </div>
                </div>
            </a>
            `)
        }
    }
}

let movieLists = $(".movie-list");

function renderMovieLists() {
    let output = [];
    $(movieLists).each(function() {
        list = $(this);
        if($(window).scrollTop() < $(list).offset().top - $(window).height()) {
            return false;
        }
        type = list.data("type");
        data_id = list.data("id");
        amount = list.data("amount");
        show = list.data("show_score") ?? 1;
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
                console.log("Rendered " + type + " list with data of " + data_id);
                displayLists(response.movies, list, show, show_name, response.category);
                movieLists.splice(0, 1);
            }
        });
    });
    return output;
}

window.onload =function() {
    renderMovieLists();
};

$(window).scroll(function() {
    renderMovieLists();
});