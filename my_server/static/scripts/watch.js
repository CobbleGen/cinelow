let categoryList = [];
let usersList = [];

$('.closed').click(function (e) { 
    if ($(this).hasClass("closed")) {
        $(this).animate({
            width: '300px',
            height: '400px',
            right: '-285px',
            top: '10px'
        });
        $(this).children("#list-of-cats").show();
        $(this).removeClass("closed");
        $(this).children("#cat-button").css({'transform' : 'rotate(-45deg)'})
    }
});

function closeCategories() {
    $("#add-category").animate({
        width: '15',
        height: '23',
        right: '0',
        top: '10px'
    });
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
}
redoClicks();



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
                                }));
                                usersList.push(e.id);
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
    
}