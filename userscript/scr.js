// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        *://www.linkedin.com/in/*
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @grant        GM_setClipboard
// ==/UserScript==

(function() {
    'use strict';

    let itext = document.body.innerText;
    let sheidx = itext.indexOf('She/Her');
    let heidx = itext.indexOf('He/Him');
    console.log('detection');
    if (sheidx === -1) {
        if (heidx === -1) {
            GM_setClipboard('LINKEDIN_CLIP_UNKNOWN', 'text');
        } else {
            GM_setClipboard('LINKEDIN_CLIP_HE', 'text');
        }
    } else {
        if (heidx === -1) {
            GM_setClipboard('LINKEDIN_CLIP_SHE', 'text');
        } else {
            if (heidx < sheidx) {
                GM_setClipboard('LINKEDIN_CLIP_HE', 'text');
            } else {
                GM_setClipboard('LINKEDIN_CLIP_SHE', 'text');
            }
        }
    }
})();
