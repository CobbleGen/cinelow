tmdb_key = "db254eee52d0c8fbc70d51368cd24644";
let movie1 = null;
let movie2 = null;

function getNewMovies() {
    $.ajax({
        type: "GET",
        url: "/_getmovies",
        dataType: "json",
        success: function (response) {
            movie1 = response.m1;
            movie2 = response.m2;
            $('#movie1-box').html($('<img>').attr('src', 'https://image.tmdb.org/t/p/w500' + movie1.poster_path));
            $('#movie2-box').html($('<img>').attr('src', 'https://image.tmdb.org/t/p/w500' + movie2.poster_path));
            $('#name1').text(movie1.name);
            $('#name2').text(movie2.name);
            let concatArray = response.common_categories.concat(response.common_people);
            console.log(concatArray);
            let out = "";
            for (let i = 1; i < concatArray.length; i++) {
                const e = concatArray[i];
                out += e.name + " movie <br />";
                console.log(e.name);
            }
            $("#common-tt").html("<a> <h4>Which is the best:</h4>" + out + "</a>");
        },
        error: function (response) {
            console.log(response);
          }
    });
}
getNewMovies();

$('#movie1-box').click(function (e) { 
    e.preventDefault();
    voteMovie(movie1.id, movie2.id);
});
$('#movie2-box').click(function (e) { 
    e.preventDefault();
    voteMovie(movie2.id, movie1.id);
});

function voteMovie(winning_id, losing_id) {
    $.ajax({
        type: "POST",
        url: "/_vote_for_movie",
        data: {
            winning_id  : winning_id,
            losing_id   : losing_id
        },
        success: function (response) {
            getNewMovies();
        }
    });
}