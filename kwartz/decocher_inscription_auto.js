// ==UserScript==
// @name        Décocher inscription auto
// @namespace   https://kwartz-server/
// @description Décoche automatiquement les ordinateurs lors de l'inscription automatique de poste dans Kwartz
// @include     https://kwartz-server:9999/hostauto.cgi
// @grant       none
// @version     1
// ==/UserScript==
//var b = window.frames["MAIN"].document.getElementsByName("leasehost");
var b = document.getElementsByName("leasehost");
for (var i=0; i < b.length; i++) {
    b[i].checked = false;
}
