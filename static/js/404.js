// On déclare une variable globale pour y stocker la dernière musique jouée
var lastPlayedMusic = "";

// La fonction sound() joue la musique et stocke son URL dans la variable globale
function sound() {
  var music = document.getElementById("musique");
  music.loop = true;
  lastPlayedMusic = music.src;
  music.play();
}

// La fonction stopsound() arrête la dernière musique jouée en réinitialisant sa source
function stopsound() {
  var music = document.getElementById("musique");
  music.pause();
  music.currentTime = 0;
  music.src = lastPlayedMusic;
}