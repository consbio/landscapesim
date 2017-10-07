// context_help.js


// Tab info
$(document).on({
    click: function(e) {
        var text = document.getElementById('x-' + this.id).textContent;
        var title = this.text;
        var text = ["<div class='header'>", this.text, "</div>", "<p class='alertify-p'>", text, "</p>"].join('')
        alertify.alert(text);
        $('.alertify-message').remove();    // Removes the extra div created, which we replace
    },
}, '.modal-item')

// Tooltip popup on context help icons
$(document).on({
    mouseenter: function (e) {
        var popup = $("#pop-up");
        var moveRight = 5;
        var moveDown = 5;
        var text = ["<div class='context_basic'>", document.getElementById('x-' + this.id).textContent, "</div>"].join('')
        popup.html(text);  // split and get last element of the id. Ids look like 'help_step_x'
        popup.show();
        $('.context_button').mousemove(function (e) {
            popup.css('top', e.pageY + moveDown).css('left', e.pageX + moveRight);
        });
    },
    mouseleave: function(e) {
        $("#pop-up").hide();
    }
}, '.context_button');
