let categoryList = [];

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