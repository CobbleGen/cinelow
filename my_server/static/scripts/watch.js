let categoryList = [];
let usersList = [];

$('.closed').click(function (e) { 
    if ($(this).hasClass("closed")) {
        console.log($('#add-category').attr('position'));
        const animation = $('#add-category').css('position') == "absolute" ?{
            width: '300px',
            height: '400px',
            right: '-285px',
            top: '10px'
        } : {
            width: '300px',
            height: '400px',
        };
        $(this).animate(animation);
        $(this).children("#list-of-cats").show();
        $(this).removeClass("closed");
        $(this).children("#cat-button").css({'transform' : 'rotate(-45deg)'})
    }
});

function closeCategories() {
    const animation = $('#add-category').css('position') == "absolute" ?{
        width: '15',
        height: '23',
        right: '0',
    } : {
        width: '15',
        height: '23',
        right: '0',
    };
    $("#add-category").animate(animation);
    $('#cat-button').css({'transform' : 'rotate(0deg)'})
    setTimeout(function() {
        $("#add-category").addClass("closed");
    }, 200);
    $("#list-of-cats").hide();
}

$('#cat-button').click(function (e) {
    let parent = $(this).parent();
    if (!$(parent).hasClass("closed")) {
        closeCategories();
    }
});



function redoClicks() {
    $(".list-remover").off("click");
    $(".cat").off("click");

    $(".list-remover").click(function() {
        parent = $(this).parent();
        let id = $(parent).data("id");
        let name = $(parent).data("name");
        categoryList.splice(categoryList.indexOf(id), 1);
        $("#list-of-cats").append(`
            <div class="cat" id="cat-${id}" data-id="${id}" data-name="${name}">
                <a>${name}</a>
            </div>
            `);
        $(parent).hide();
        redoClicks();
    });

    $(".cat").click(function () {
        let id = $(this).data("id");
        let name = $(this).data("name");
        categoryList.push(id);
        $("#category-list").append(`
            <div class="category-item" data-id="${id}" data-name="${name}">
                <a>${name}</a>
                <i class="fas fa-times list-remover"></i>
            </div>
            `);
        $(this).hide();
        closeCategories();
        redoClicks();
    });
    generateNewMovies();
}



const uid = $(".user-prof").data("id");
if (uid) {
    usersList.push(uid);
    $(".user-prof").click(function () {
        usersList.splice(usersList.indexOf(uid), 1);
        $(this).hide();
    });
}


//Visa sökrutan om det står något i sökfältet när det klickas
$("#user-search").focus(function (e) { 
    if ($(this).val() != "") {
        $("#user-search-results").show();
    }
});

//Fokuserad på sökfältet?
$("#user-search").focusout(function (e) {
    if ($("#user-search-results:hover").length == 0) {
        $("#user-search-results").hide();
    }
});

//Släpper en bokstav på sökfältet
$("#user-search").keyup(function (e) { 
    $("#user-search-results").show();
    clearTimeout(timeout);
    if ($("#user-search").val() == "") {
        $("#user-search-results").hide();
    } else {
        timeout = setTimeout(function() {
            //Get movie info based on search query
            $.ajax({
                type: "GET",
                url: "/_search_user",
                data: {
                    query: $("#user-search").val()

                },
                dataType: "json",
                success: function (response) {
                    $("#user-search-results").empty();
                    for (let i = 0; i < response.length; i++) {
                        const e = response[i];
                        newDiv = $("<div>").html(`
                            <div class="searched-user" data-id="${e.id} data-image="${e.image_file}">
                                <img src="/static/profilepics/${e.image_file}" alt="user-img">
                                <a>${e.username}</a>
                            </div>
                        `).click(function() {
                            if (!(usersList.indexOf(e.id) >= 0)) {
                                $("#user-list").append( newDiv = $("<div>").html(`
                                    <div class="user-prof" data-id="${e.id}">
                                        <img src="/static/profilepics/${e.image_file}" alt="user-img">
                                        <i class="fas fa-times"></i>
                                    </div>
                                `).click(function () {
                                    usersList.splice(usersList.indexOf(e.id), 1);
                                    $(this).hide();
                                    generateNewMovies();
                                }));
                                usersList.push(e.id);
                                generateNewMovies();
                            }
                        });
                        $("#user-search-results").append(newDiv);
                        
                    }
                }
            });
        }, 150);
    }
});

function generateNewMovies() {
    $.ajax({
        type: "POST",
        url: "/_advanced_recommendations",
        contentType: 'application/json',
        data: JSON.stringify({
            'user_ids' : usersList,
            'category_ids': categoryList
        }),
        dataType: "JSON",
        success: function (r) {
            $("#movies-box").empty();
            for (let i = 0; i < r.length; i++) {
                const movie = r[i];
                $.ajax({
                    type: "GET",
                    url: "https://api.themoviedb.org/3/movie/" + movie.id,
                    data: {
                        api_key  : "db254eee52d0c8fbc70d51368cd24644"
                    },
                    dataType: "JSON",
                    success: function (response) {
                        $("#movies-box").append(`
                            <a href="/m/${movie.id}">
                                <div class="rec-movie">
                                    <img src="https://image.tmdb.org/t/p/w94_and_h141_bestv2${movie.poster_path}" alt="">
                                    <h1>${movie.name}</h1>
                                    <p>${response.overview}</p>
                                </div>
                            </a>
                        `);
                    }
                });
            }
        },
        error: function(r) {
            console.error(r);
        }
    });
}

redoClicks();
