tmdb_key = "db254eee52d0c8fbc70d51368cd24644";
let movie1 = null;
let movie2 = null;

function getNewMovies() {
    $.ajax({
        type: "GET",
        url: "/_getmovies",
        dataType: "json",
        success: function (response) {
            $.ajax({
                type: "GET",
                url: "https://api.themoviedb.org/3/movie/" + response.m1,
                data: {
                    api_key: tmdb_key,
                    language: "en-US"
                },
                dataType: "json",
                success: function (response2) {
                    movie1 = response2;
                    $.ajax({
                        type: "GET",
                        url: "https://api.themoviedb.org/3/movie/" + response.m2,
                        data: {
                            api_key: tmdb_key,
                            language: "en-US"
                        },
                        dataType: "json",
                        success: function (response) {
                            movie2 = response;
                            $('#movie1-box').html($('<img>').attr('src', 'https://image.tmdb.org/t/p/w500' + movie1.poster_path));
                            $('#movie2-box').html($('<img>').attr('src', 'https://image.tmdb.org/t/p/w500' + movie2.poster_path));
                            console.log(movie1);
                            console.log(movie2);
                        }
                    });
                }
            });
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