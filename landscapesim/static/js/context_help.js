// Tab info
$(document).on({
    click: function() {
        var text = [
            "<div class='alertify-scrollable-div'>",
            document.getElementById('x-' + this.id).textContent,
            "</div>"
        ].join('');
        var title = this.text;
        var text = ["<div class='alertify-header'>", this.text, "</div>", text].join('')
        alertify.alert(text);
        $('.alertify-message').remove();    // Removes the extra div created, which we replace
    },
}, '.modal-item')

// Tooltip popup on context help icons
$(document).on({
    mouseenter: function (e) {
        var popup = $("#pop-up");
        var moveRight = 10;
        var moveDown = 10;
        var id = this.children[0].id;
        var text = ["<div class='context_basic'>", document.getElementById('x-' + id).textContent, "</div>"].join('')
        popup.html(text);  // split and get last element of the id. Ids look like 'help_step_x'
        popup.show();
        $('#left .header').mousemove(function (e) {
            popup.css('top', e.pageY + moveDown).css('left', e.pageX + moveRight);
        });
    },
    mouseleave: function(e) {
        $("#pop-up").hide();
    }
}, '#left .header');

// Allow dismiss on click
$(document).on({
    click: function(e) {
        document.getElementById('alertify-ok').click();
    }
}, '#alertify-cover');
