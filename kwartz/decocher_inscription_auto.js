// ==UserScript==
// @name        D�cocher inscription auto
// @namespace   https://kwartz-server.jeanmoulin.fr
// @description D�coche automatiquement les ordinateurs lors de l'inscription automatique de poste dans Kwartz
// @include     https://kwartz-server.jeanmoulin.fr:9999/hostauto.cgi
// @version     1
// ==/UserScript==
//var b = window.frames["MAIN"].document.getElementsByName("leasehost");
var b = document.getElementsByName("leasehost");
for (var i=0; i < b.length; i++) {
    b[i].checked = false;
}